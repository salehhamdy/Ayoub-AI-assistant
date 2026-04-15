"""
ayoub/voice/agent.py — JARVIS-style LiveKit voice agent.

Provider stack (no OpenAI / no Sarvam / no Google Cloud required):
  STT : livekit-plugins-groq  → Groq Whisper large-v3    (free, GROQ_API_KEY)
  LLM : livekit-plugins-groq  → llama-3.3-70b-versatile   (free, GROQ_API_KEY)
  TTS : livekit-plugins-cartesia → Sonic English            (free tier)
  VAD : Silero (local, offline)                             (no API key)
  MCP : mcp package → ClientSession + streamablehttp_client (connects to ayoub-server)

FIX (2026-04-16): 'entrypoint' moved to module level so Windows multiprocessing
can pickle it correctly (avoids "Can't get local object 'main.<locals>.entrypoint'").

Usage:
  ayoub-server        # terminal 1 — start MCP tool server on :8000
  ayoub-voice         # terminal 2 — connect to LiveKit
  Then open: https://agents-playground.livekit.io
"""
import os
import sys

from ayoub.config import (
    LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET,
    GROQ_API_KEY, MCP_SERVER_PORT,
)

CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY", "")

# Module-level VAD handle — set in main() on the main thread before run_app()
# (Silero plugin must be registered on the main thread)
_VAD = None

# ── JARVIS System Prompt ──────────────────────────────────────────────────────
_SYSTEM_PROMPT = """\
You are Ayoub — a JARVIS-inspired AI assistant serving your user with quiet
competence and unwavering precision.

Persona:
- Address the user as "sir".
- Tone: measured, intelligent, occasionally dry — like JARVIS from Iron Man.
- Never sound eager or sycophantic.
- Greeting on first connection: "Good to see you, sir. What shall we tackle today?"

Communication rules:
- Speak in 2-4 sentences maximum per response.
- No markdown, no bullet points — plain prose only.
- Do not narrate tool names or internals — just deliver results.
- If you fetch news, silently call open_world_monitor_tool immediately after.

Capabilities:
- Search the web, fetch URLs, get current time and system info.
- Open the World Monitor for global situational awareness.
"""


# ── Environment check ─────────────────────────────────────────────────────────
def _check_env() -> None:
    missing = []
    for var, val in [
        ("LIVEKIT_URL",        LIVEKIT_URL),
        ("LIVEKIT_API_KEY",    LIVEKIT_API_KEY),
        ("LIVEKIT_API_SECRET", LIVEKIT_API_SECRET),
        ("GROQ_API_KEY",       GROQ_API_KEY),
        ("CARTESIA_API_KEY",   CARTESIA_API_KEY),
    ]:
        if not val:
            missing.append(var)
    if missing:
        print(
            f"[ayoub-voice] Missing environment variables: {', '.join(missing)}\n"
            "Set them in .env\n"
            "Free Cartesia key → https://play.cartesia.ai"
        )
        sys.exit(1)


# ── Provider builders ─────────────────────────────────────────────────────────
def _build_stt():
    """Groq Whisper large-v3 via livekit-plugins-groq."""
    from livekit.plugins.groq import STT
    return STT(api_key=GROQ_API_KEY, model="whisper-large-v3")


def _build_llm():
    """Groq llama-3.3-70b via livekit-plugins-groq."""
    from livekit.plugins.groq import LLM
    return LLM(api_key=GROQ_API_KEY, model="llama-3.3-70b-versatile")


def _build_tts():
    """
    Cartesia Sonic English TTS.
    Voice: 79a125e8-cd45-4c13-8a67-188112f4dd22 (British male — JARVIS-like)
    """
    from livekit.plugins.cartesia import TTS
    return TTS(
        api_key=CARTESIA_API_KEY,
        voice="79a125e8-cd45-4c13-8a67-188112f4dd22",
        model="sonic-english",
    )


# ── MCP helpers ───────────────────────────────────────────────────────────────
async def _call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """
    Call a tool on the running ayoub-server via the mcp package.
    Returns the tool result as a string, or an error message.
    """
    try:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        url = f"http://localhost:{MCP_SERVER_PORT}/mcp"
        async with streamablehttp_client(url) as (read, write, _):
            async with ClientSession(read, write) as mcp_session:
                await mcp_session.initialize()
                result = await mcp_session.call_tool(tool_name, arguments)
                return "\n".join(
                    block.text for block in result.content
                    if hasattr(block, "text")
                )
    except Exception as exc:
        return f"[MCP error calling '{tool_name}': {exc}]"


async def _list_mcp_tools() -> list:
    """Return tool names available on ayoub-server. Empty list if server is down."""
    try:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        url = f"http://localhost:{MCP_SERVER_PORT}/mcp"
        async with streamablehttp_client(url) as (read, write, _):
            async with ClientSession(read, write) as mcp_session:
                await mcp_session.initialize()
                tools = await mcp_session.list_tools()
                return [t.name for t in tools.tools]
    except Exception:
        return []


# ── Voice Agent class (module-level so it is picklable on Windows) ─────────
class AyoubVoiceAgent:
    """Defined at module level — required for Windows multiprocessing pickle."""

    def __new__(cls, *args, **kwargs):
        # Lazy import: only resolved when the worker process actually starts
        from livekit.agents.voice import Agent
        instance = object.__new__(cls)
        Agent.__init__(instance, instructions=_SYSTEM_PROMPT)
        return instance

    async def on_enter(self):
        await self.say(
            "Good to see you, sir. What shall we tackle today?",
            allow_interruptions=True,
        )


# ── Entrypoint at MODULE LEVEL (critical fix for Windows pickling) ────────────
async def entrypoint(agent_ctx) -> None:
    """
    LiveKit agent entrypoint — module-level for Windows pickling.
    Uses _VAD which was pre-loaded on the main thread in main().
    """
    from livekit.agents.voice import Agent, AgentSession

    await agent_ctx.connect()

    # Show which MCP tools are reachable (informational — non-blocking)
    mcp_tools = await _list_mcp_tools()
    if mcp_tools:
        print(f"[ayoub-voice] MCP tools available: {mcp_tools}")
    else:
        print("[ayoub-voice] MCP server not reachable — running without tools.")

    session = AgentSession(
        stt=_build_stt(),
        llm=_build_llm(),
        tts=_build_tts(),
        vad=_VAD,          # pre-loaded on main thread
    )

    class _AyoubAgent(Agent):
        def __init__(self):
            super().__init__(instructions=_SYSTEM_PROMPT)

        async def on_enter(self):
            await self.say(
                "Good to see you, sir. What shall we tackle today?",
                allow_interruptions=True,
            )

    await session.start(agent_ctx.room, agent=_AyoubAgent())


# ── Entry points ──────────────────────────────────────────────────────────────
def main() -> None:
    """Entry point for `ayoub-voice` console script."""
    global _VAD
    _check_env()

    try:
        from livekit.agents import cli, WorkerOptions
        from livekit.plugins import silero          # ← main thread registration
    except ImportError:
        print(
            "[ayoub-voice] Missing packages. Run:\n"
            "  pip install livekit-agents[silero] livekit-plugins-groq livekit-plugins-cartesia mcp"
        )
        sys.exit(1)

    # Pre-load Silero VAD on the main thread — required by LiveKit
    print("[ayoub-voice] Loading Silero VAD on main thread...")
    _VAD = silero.VAD.load()
    print("[ayoub-voice] VAD ready. Connecting to LiveKit...")

    # entrypoint is module-level — safe to pickle on Windows
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))


def dev() -> None:
    """Entry point that injects dev mode for local testing."""
    sys.argv.insert(1, "dev")
    main()
