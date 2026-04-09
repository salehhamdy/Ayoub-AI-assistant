"""
ayoub/voice/agent.py — JARVIS-style LiveKit voice agent.

Ported and renamed from friday-tony-stark-demo/agent_friday.py
Persona: Ayoub / JARVIS — calm, precise, addresses user as "sir".

Requirements (optional — only needed for voice mode):
  pip install livekit-agents livekit-plugins-google livekit-plugins-sarvam
  Set in .env: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET,
               SARVAM_API_KEY, STT_PROVIDER, TTS_PROVIDER

Usage:
  ayoub-voice        # from CLI after uv sync
"""
import os
import sys

from ayoub.config import (
    LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET,
    SARVAM_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY,
    STT_PROVIDER, TTS_PROVIDER, MCP_SERVER_PORT,
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
- No markdown, no bullet points, no list items in spoken replies.
- Do not narrate tool names or technical internals — just deliver results.
- If you fetch news, immediately after summarising, silently call open_world_monitor_tool.

Capabilities:
- You can search the web, fetch URLs, get the time and system info.
- You can open the World Monitor for global situational awareness.
- You remember the context within this session.
"""


def _check_env() -> None:
    """Warn if required environment variables are missing."""
    missing = []
    for var in ("LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"):
        if not os.getenv(var):
            missing.append(var)
    if missing:
        print(
            f"[ayoub-voice] WARNING: Missing environment variables: {', '.join(missing)}\n"
            "Set them in .env before running ayoub-voice."
        )


def main() -> None:
    """
    Entry point for ayoub-voice console script.
    Initialises the LiveKit voice agent with the configured STT/LLM/TTS providers.
    """
    _check_env()

    try:
        from livekit.agents import cli, WorkerOptions, ctx
        from livekit.agents.voice import Agent, AgentSession
        from livekit.plugins import silero
    except ImportError:
        print(
            "[ayoub-voice] livekit-agents is not installed.\n"
            "Run: pip install 'livekit-agents[openai,silero]'"
        )
        sys.exit(1)

    def _build_stt():
        if STT_PROVIDER == "sarvam":
            try:
                from livekit.plugins.sarvam import STT
                return STT(api_key=SARVAM_API_KEY, model="saaras:v3", language="en-IN")
            except ImportError:
                pass
        from livekit.plugins.openai import STT as WhisperSTT
        return WhisperSTT(api_key=OPENAI_API_KEY)

    def _build_llm():
        try:
            from livekit.plugins.google import LLM as GeminiLLM
            return GeminiLLM(api_key=GOOGLE_API_KEY, model="gemini-2.5-flash")
        except ImportError:
            from livekit.plugins.openai import LLM as OpenAILLM
            return OpenAILLM(api_key=OPENAI_API_KEY, model="gpt-4o")

    def _build_tts():
        if TTS_PROVIDER == "sarvam":
            try:
                from livekit.plugins.sarvam import TTS
                return TTS(api_key=SARVAM_API_KEY, model="bulbul:v3", language="en-IN")
            except ImportError:
                pass
        from livekit.plugins.openai import TTS as OpenAITTS
        return OpenAITTS(api_key=OPENAI_API_KEY, voice="nova")

    def _build_mcp():
        try:
            from livekit.agents.mcp import MCPServerHTTP
            return [MCPServerHTTP(url=f"http://localhost:{MCP_SERVER_PORT}/sse")]
        except ImportError:
            return []

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
