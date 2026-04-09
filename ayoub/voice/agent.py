"""
ayoub/voice/agent.py — JARVIS-style LiveKit voice agent.

Provider stack (no OpenAI / no Sarvam required):
  STT : Groq Whisper (whisper-large-v3) — free with GROQ_API_KEY
  LLM : Google Gemini 2.5 Flash        — free tier with GOOGLE_API_KEY
  TTS : Google Cloud TTS               — free tier with GOOGLE_API_KEY
  VAD : Silero (local, no API key)

Usage:
  ayoub-server        # terminal 1 — start MCP tool server
  ayoub-voice         # terminal 2 — connect to LiveKit
  Then open: https://agents-playground.livekit.io
"""
import os
import sys

from ayoub.config import (
    LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET,
    GOOGLE_API_KEY, GROQ_API_KEY,
    STT_PROVIDER, TTS_PROVIDER,
    MCP_SERVER_PORT,
)

# ── JARVIS System Prompt ──────────────────────────────────────────────────────
_SYSTEM_PROMPT = """\
You are Ayoub — a JARVIS-inspired AI assistant serving your user with quiet
competence and unwavering precision.

Persona:
- Address the user as "sir" (not by name, not "boss").
- Tone: measured, intelligent, occasionally dry — like JARVIS from Iron Man.
- Never sound eager or sycophantic.
- Greeting on first connection: "Good to see you, sir. What shall we tackle today?"

Communication rules:
- Speak in 2-4 sentences maximum per response.
- No markdown, no bullet points, no lists in spoken replies — plain prose only.
- Do not narrate tool names or technical internals — just deliver results.
- If you fetch news, silently call open_world_monitor_tool immediately after summarising.

Capabilities:
- You can search the web, fetch URLs, get the current time and system info.
- You can open the World Monitor for global situational awareness.
- You remember context within this session.
"""


def _check_env() -> None:
    missing = []
    for var, val in [
        ("LIVEKIT_URL", LIVEKIT_URL),
        ("LIVEKIT_API_KEY", LIVEKIT_API_KEY),
        ("LIVEKIT_API_SECRET", LIVEKIT_API_SECRET),
        ("GOOGLE_API_KEY", GOOGLE_API_KEY),
        ("GROQ_API_KEY", GROQ_API_KEY),
    ]:
        if not val:
            missing.append(var)
    if missing:
        print(
            f"[ayoub-voice] Missing environment variables: {', '.join(missing)}\n"
            "Set them in .env before running ayoub-voice."
        )
        sys.exit(1)


def _build_stt():
    """
    STT selection:
      groq   → Groq Whisper large-v3 (fastest, free with GROQ_API_KEY)
      google → Google Cloud STT (fallback, uses GOOGLE_API_KEY / service account)
    """
    if STT_PROVIDER == "groq":
        try:
            from livekit.plugins.openai import STT
            # Groq's API is OpenAI-compatible — point Whisper at Groq's endpoint
            return STT(
                api_key=GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
                model="whisper-large-v3",
            )
        except Exception as exc:
            print(f"[ayoub-voice] Groq STT failed ({exc}), falling back to Google.")

    # Google STT fallback
    try:
        from livekit.plugins.google import STT
        return STT()   # uses GOOGLE_APPLICATION_CREDENTIALS or API key
    except Exception as exc:
        raise RuntimeError(f"[ayoub-voice] Could not load any STT provider: {exc}")


def _build_llm():
    """LLM: Google Gemini 2.5 Flash (fast, free tier)."""
    try:
        from livekit.plugins.google import LLM
        return LLM(model="gemini-2.5-flash", api_key=GOOGLE_API_KEY)
    except Exception as exc:
        raise RuntimeError(f"[ayoub-voice] Could not load Gemini LLM: {exc}")


def _build_tts():
    """
    TTS selection:
      google → Google Cloud TTS (free tier, uses GOOGLE_API_KEY)
    Voices: en-US-Neural2-D (male, deep — JARVIS-like)
    """
    if TTS_PROVIDER == "google":
        try:
            from livekit.plugins.google import TTS
            return TTS(
                voice_name="en-US-Neural2-D",   # deep male JARVIS voice
                language="en-US",
            )
        except Exception as exc:
            print(f"[ayoub-voice] Google TTS unavailable ({exc}).")

    raise RuntimeError(
        "[ayoub-voice] No TTS provider available.\n"
        "Make sure livekit-plugins-google is installed: pip install livekit-plugins-google"
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
            "Run: pip install 'livekit-agents[openai,silero]' livekit-plugins-google"
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
    """Entry point that injects 'dev' mode for local testing."""
    sys.argv.insert(1, "dev")
    main()
