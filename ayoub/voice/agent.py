"""
ayoub/voice/agent.py — JARVIS-style LiveKit voice agent.

Provider stack:
  STT : livekit-plugins-groq  → Groq Whisper large-v3      (free, GROQ_API_KEY)
  LLM : livekit-plugins-groq  → llama-3.3-70b-versatile    (free, GROQ_API_KEY)
  TTS : livekit-plugins-cartesia → Sonic English            (free tier)
  VAD : Silero (local, offline)                             (no API key)
  MCP : mcp package → ClientSession + streamablehttp_client

CONFIRMED FIX (2026-04-16) for Windows:
  livekit-agents 1.5.x calls prewarm_fnc from a DAEMON THREAD, not the main
  thread. Plugin.register_plugin() requires the main thread.

  The ONLY code that runs on the main thread of the spawned worker process is
  MODULE-LEVEL code — executed when Python imports this module to unpickle
  the 'entrypoint' function.

  Solution: ALL plugin imports are at module level.
  prewarm() only loads the VAD model (no plugin imports there).

Usage:
  ayoub-server        # terminal 1 — MCP tool server on :8000
  ayoub-voice         # terminal 2 — connect to LiveKit Cloud
  Then open https://agents-playground.livekit.io (Agent name: ayoub)
"""
import asyncio
import os
import sys

from ayoub.config import (
    LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET,
    GROQ_API_KEY, MCP_SERVER_PORT,
    OPENAI_API_KEY,
)

CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY", "")
VOICE_PROVIDER   = os.getenv("VOICE_PROVIDER", "groq")  # groq | openai

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE-LEVEL PLUGIN IMPORTS  ← DO NOT move these into any function
# ───────────────────────────────────────────────────────────────────────────────
# Each livekit plugin's __init__.py calls Plugin.register_plugin() at IMPORT
# TIME. This must happen on the main thread. Module-level code runs on the main
# thread of the spawned worker when Python imports this file to unpickle
# 'entrypoint'. Running them here is the only reliable cross-platform fix.
# ═══════════════════════════════════════════════════════════════════════════════
try:
    from livekit.agents import AutoSubscribe
    from livekit.agents.voice import Agent, AgentSession
    from livekit.plugins.groq import STT as GroqSTT, LLM as GroqLLM
    from livekit.plugins.cartesia import TTS as CartesiaTTS
    from livekit.plugins.openai import STT as OpenAISTT, LLM as OpenAILLM, TTS as OpenAITTS
    from livekit.plugins import silero
    _PLUGINS_READY = True
except ImportError as _import_err:
    _PLUGINS_READY = False
    _import_err_msg = str(_import_err)

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
            async with ClientSession(read, write) as s:
                await s.initialize()
                result = await s.call_tool(tool_name, arguments)
                return "\n".join(
                    b.text for b in result.content if hasattr(b, "text")
                )
    except Exception as exc:
        return f"[MCP error: {exc}]"


async def _list_mcp_tools() -> list:
    try:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client
        url = f"http://localhost:{MCP_SERVER_PORT}/mcp"
        async with streamablehttp_client(url) as (read, write, _):
            async with ClientSession(read, write) as s:
                await s.initialize()
                tools = await s.list_tools()
                return [t.name for t in tools.tools]
    except Exception:
        return []


# ── Prewarm — VAD model loading ONLY (plugins already registered at module level)
def prewarm(proc) -> None:
    """
    Load the Silero VAD model and store it in proc.userdata.
    Plugin registration already happened at module-import time above.
    DO NOT import livekit plugins here — this runs in a daemon thread.
    """
    if not _PLUGINS_READY:
        return
    print("[ayoub-voice] Prewarm: loading Silero VAD model...")
    proc.userdata["vad"] = silero.VAD.load()
    print("[ayoub-voice] VAD model loaded.")


# ── Entrypoint — module-level so it can be pickled on Windows ─────────────────
async def entrypoint(ctx) -> None:
    """LiveKit job entrypoint. Plugins registered at module level, VAD from prewarm."""
    if not _PLUGINS_READY:
        print(f"[ayoub-voice] ERROR: voice plugins not installed. {_import_err_msg}")
        return

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    mcp_tools = await _list_mcp_tools()
    print(f"[ayoub-voice] MCP: {mcp_tools or 'no tools (server not running)'}")

    print("[ayoub-voice] Waiting for participant...")
    participant = await ctx.wait_for_participant()
    print(f"[ayoub-voice] Participant joined: {participant.identity}")

    vad = ctx.proc.userdata.get("vad")

    # ── Voice provider selection ──────────────────────────────────────────────
    if VOICE_PROVIDER == "openai":
        print("[ayoub-voice] Using OpenAI voice stack (STT + LLM + TTS)")
        stt = OpenAISTT(api_key=OPENAI_API_KEY)
        llm = OpenAILLM(api_key=OPENAI_API_KEY, model="gpt-4o-mini")
        tts = OpenAITTS(api_key=OPENAI_API_KEY, voice="onyx")  # onyx = deep male voice
    else:
        print("[ayoub-voice] Using Groq+Cartesia voice stack (default)")
        stt = GroqSTT(api_key=GROQ_API_KEY, model="whisper-large-v3")
        llm = GroqLLM(api_key=GROQ_API_KEY, model="llama-3.3-70b-versatile")
        tts = CartesiaTTS(
            api_key=CARTESIA_API_KEY,
            voice="79a125e8-cd45-4c13-8a67-188112f4dd22",
            model="sonic-english",
        )

    session = AgentSession(stt=stt, llm=llm, tts=tts, vad=vad)

    class _AyoubAgent(Agent):
        def __init__(self):
            super().__init__(instructions=_SYSTEM_PROMPT)

        async def on_enter(self):
            await asyncio.sleep(1)
            await self.say(
                "Good to see you, sir. What shall we tackle today?",
                allow_interruptions=True,
            )

    # agent is first positional arg; participant= not supported in livekit-agents 1.5.x
    await session.start(_AyoubAgent(), room=ctx.room)


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

    print("[ayoub-voice] Starting — plugins registered at module import...")
    print(f"[ayoub-voice] Voice provider: {VOICE_PROVIDER}  (set VOICE_PROVIDER=openai to switch)")
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
        # agent_name="" (empty) = implicit dispatch — playground auto-dispatches to this worker
    ))


def dev() -> None:
    """Entry point that injects dev mode for local testing."""
    sys.argv.insert(1, "dev")
    main()
