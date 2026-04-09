"""
ayoub/voice/agent.py — JARVIS-style LiveKit voice agent.

Provider stack (no OpenAI / no Sarvam / no Google Cloud required):
  STT : Groq Whisper large-v3     — free with GROQ_API_KEY  ✅
  LLM : Groq llama-3.3-70b        — free with GROQ_API_KEY  ✅
  TTS : Cartesia (Sonic English)   — free tier, get key at play.cartesia.ai ✅
  VAD : Silero (local, offline)    — no API key needed       ✅

Get your free Cartesia key:
  1. Go to https://play.cartesia.ai
  2. Sign up (free, no credit card)
  3. Copy API key → add to .env as CARTESIA_API_KEY=...

Usage:
  ayoub-server        # terminal 1 — start MCP tool server
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
- If you fetch news, silently call open_world_monitor_tool immediately after.

Capabilities:
- Search the web, fetch URLs, get current time and system info.
- Open the World Monitor for global situational awareness.
"""


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


def _build_stt():
    """
    Groq Whisper large-v3 via the OpenAI-compatible plugin.
    Fastest transcription available, free with GROQ_API_KEY.
    """
    from livekit.plugins.openai import STT
    return STT(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        model="whisper-large-v3",
    )


def _build_llm():
    """
    Groq llama-3.3-70b via the OpenAI-compatible plugin.
    Very fast, free with GROQ_API_KEY.
    """
    from livekit.plugins.openai import LLM
    return LLM(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
    )


def _build_tts():
    """
    Cartesia Sonic English TTS — natural, fast, free tier available.
    Get key: https://play.cartesia.ai
    Voice ID: 79a125e8-cd45-4c13-8a67-188112f4dd22  (British man — JARVIS-like)
    """
    from livekit.plugins.cartesia import TTS
    return TTS(
        api_key=CARTESIA_API_KEY,
        voice="79a125e8-cd45-4c13-8a67-188112f4dd22",  # British male, deep
        model="sonic-english",
    )


def _build_mcp():
    try:
        from livekit.agents.mcp import MCPServerHTTP
        return [MCPServerHTTP(url=f"http://localhost:{MCP_SERVER_PORT}/sse")]
    except ImportError:
        return []


def main() -> None:
    """Entry point for `ayoub-voice` console script."""
    _check_env()

    try:
        from livekit.agents import cli, WorkerOptions, ctx
        from livekit.agents.voice import Agent, AgentSession
        from livekit.plugins import silero
    except ImportError:
        print(
            "[ayoub-voice] livekit-agents is not installed.\n"
            "Run: pip install -r requirements.txt"
        )
        sys.exit(1)

    async def entrypoint(agent_ctx: ctx.JobContext) -> None:
        await agent_ctx.connect()

        session = AgentSession(
            stt=_build_stt(),
            llm=_build_llm(),
            tts=_build_tts(),
            vad=silero.VAD.load(),
            mcp_servers=_build_mcp(),
        )

        class AyoubVoiceAgent(Agent):
            def __init__(self):
                super().__init__(instructions=_SYSTEM_PROMPT)

            async def on_enter(self):
                await self.say(
                    "Good to see you, sir. What shall we tackle today?",
                    allow_interruptions=True,
                )

        await session.start(agent_ctx.room, agent=AyoubVoiceAgent())

    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))


def dev() -> None:
    """Entry point that injects dev mode for local testing."""
    sys.argv.insert(1, "dev")
    main()
