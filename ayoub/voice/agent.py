"""
ayoub/voice/agent.py — JARVIS-style LiveKit voice agent.

Provider stack:
  STT : livekit-plugins-groq  → Groq Whisper large-v3    (free, GROQ_API_KEY)
  LLM : livekit-plugins-groq  → llama-3.3-70b-versatile   (free, GROQ_API_KEY)
  TTS : livekit-plugins-cartesia → Sonic English            (free tier)
  VAD : Silero (local, offline)                             (no API key)
  MCP : mcp package → ClientSession + streamablehttp_client

FIX (2026-04-16): All plugins are registered inside prewarm_fnc(), which LiveKit
guarantees runs on the main thread of each worker process. This avoids the
"Plugins must be registered on the main thread" RuntimeError on Windows.

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


# ── MCP helpers ───────────────────────────────────────────────────────────────
async def _call_mcp_tool(tool_name: str, arguments: dict) -> str:
    try:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        url = f"http://localhost:{MCP_SERVER_PORT}/mcp"
        async with streamablehttp_client(url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return "\n".join(
                    block.text for block in result.content
                    if hasattr(block, "text")
                )
    except Exception as exc:
        return f"[MCP error calling '{tool_name}': {exc}]"


async def _list_mcp_tools() -> list:
    try:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        url = f"http://localhost:{MCP_SERVER_PORT}/mcp"
        async with streamablehttp_client(url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return [t.name for t in tools.tools]
    except Exception:
        return []


# ── Prewarm function — runs on main thread of each worker process ─────────────
# This is the CORRECT place to register LiveKit plugins. LiveKit calls this
# before dispatching any job, guaranteed on the main thread.
async def prewarm(proc) -> None:
    """
    Pre-warm function: import + register all plugins on the worker's main thread.
    Store heavy objects in proc.userdata so entrypoint() can reuse them.
    """
    # Importing these registers the plugins on the main thread of this process
    from livekit.plugins.groq import STT, LLM          # also registers openai plugin
    from livekit.plugins.cartesia import TTS
    from livekit.plugins import silero

    print("[ayoub-voice] Prewarm: loading Silero VAD...")
    proc.userdata["vad"] = silero.VAD.load()
    print("[ayoub-voice] Prewarm complete — plugins registered, VAD ready.")


# ── Entrypoint — module-level for Windows pickling ───────────────────────────
async def entrypoint(ctx) -> None:
    """
    LiveKit job entrypoint. All plugins are already registered via prewarm().
    Imports here are safe — they resolve from cache, no re-registration.
    """
    from livekit.agents.voice import Agent, AgentSession
    from livekit.plugins.groq import STT, LLM
    from livekit.plugins.cartesia import TTS

    await ctx.connect()

    mcp_tools = await _list_mcp_tools()
    if mcp_tools:
        print(f"[ayoub-voice] MCP tools available: {mcp_tools}")
    else:
        print("[ayoub-voice] MCP server not reachable — running without tools.")

    # Retrieve the pre-loaded VAD from prewarm userdata
    vad = ctx.proc.userdata.get("vad")

    session = AgentSession(
        stt=STT(api_key=GROQ_API_KEY, model="whisper-large-v3"),
        llm=LLM(api_key=GROQ_API_KEY, model="llama-3.3-70b-versatile"),
        tts=TTS(
            api_key=CARTESIA_API_KEY,
            voice="79a125e8-cd45-4c13-8a67-188112f4dd22",
            model="sonic-english",
        ),
        vad=vad,
    )

    class _AyoubAgent(Agent):
        def __init__(self):
            super().__init__(instructions=_SYSTEM_PROMPT)

        async def on_enter(self):
            await self.say(
                "Good to see you, sir. What shall we tackle today?",
                allow_interruptions=True,
            )

    await session.start(ctx.room, agent=_AyoubAgent())


# ── Entry points ──────────────────────────────────────────────────────────────
def main() -> None:
    """Entry point for `ayoub-voice` console script."""
    _check_env()

    try:
        from livekit.agents import cli, WorkerOptions
    except ImportError:
        print(
            "[ayoub-voice] Missing packages. Run:\n"
            "  pip install livekit-agents[silero] livekit-plugins-groq livekit-plugins-cartesia mcp"
        )
        sys.exit(1)

    print("[ayoub-voice] Starting — plugins will be registered in prewarm...")
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,       # ← registers all plugins on main thread of each worker
    ))


def dev() -> None:
    """Entry point that injects dev mode for local testing."""
    sys.argv.insert(1, "dev")
    main()
