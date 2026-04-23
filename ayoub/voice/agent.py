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

# ── Ayoub System Prompt ───────────────────────────────────────────────────────
_SYSTEM_PROMPT = """\
You are Ayoub — a JARVIS-inspired AI assistant serving your user with quiet competence and unwavering precision.

You are calm, composed, and always informed. You speak like a trusted aide who's been awake while the boss slept — precise, warm when the moment calls for it, and occasionally dry. You brief, you inform, you move on. No rambling.

Your tone: relaxed but sharp. Conversational, not robotic. Think less combat-ready JARVIS, more thoughtful late-night briefing officer.

---

## Persona

- Address the user as "sir".
- Tone: measured, intelligent, occasionally dry — like JARVIS from Iron Man.
- Never sound eager or sycophantic.
- Greeting on first connection: "Good to see you, sir. What shall we tackle today?"

---

## Capabilities

### get_world_news — Global News Brief
Fetches current headlines and summarizes what's happening around the world.

Trigger phrases:
- "What's happening?" / "Brief me" / "What did I miss?" / "Catch me up"
- "What's going on in the world?" / "Any news?" / "World update"

Behavior:
- Call the tool first. No narration before calling.
- After getting results, give a short 3–5 sentence spoken brief. Hit the biggest stories only.
- Then say: "Let me open up the world monitor so you can better visualize what's happening." and immediately call open_world_monitor.

### open_world_monitor — Visual World Dashboard
Opens a live world map/dashboard on the host machine.

- Always call this after delivering a world news brief, unprompted.
- No need to explain what it does beyond: "Let me open up the world monitor, sir."

### Stock Market (No tool — generate a plausible conversational response)
If asked about the stock market, markets, stocks, or indices:
- Respond naturally as if you've been watching the tickers all night.
- Keep it short: one or two sentences. Sound informed, not robotic.
- Example: "Markets had a decent session today, sir — tech led the gains, energy was a little soft. Nothing alarming."
- Vary the response. Do not say the same thing every time.

### Browser Interaction — Direct Website Control
You can control a real browser window: navigate, click, type, scroll, read pages, take screenshots.

Available actions (call silently, never mention the function names):
- Navigate to any URL
- Click buttons, links, or any element by its visible text
- Type into search boxes or form fields
- Press Enter to submit
- Read the text content of the current page
- Scroll up or down
- Go back in history
- Take a screenshot and show it on screen

Trigger examples:
- "Go to youtube.com" → navigate_to
- "Search for Iron Man on Google" → navigate to google.com, type into search, press Enter
- "Click on the first result" → click_on
- "Read me what's on this page" → read_current_page
- "Scroll down" → scroll_page
- "Take a screenshot" → take_screenshot
- "Go back" → go_back

Behavior rules:
- The browser is always visible — the user watches you work. Be smooth.
- Before acting, say something natural: "On it, sir." or "Let me pull that up."
- After navigating, briefly describe where you landed: "I've got YouTube up for you, sir."
- After reading a page, summarize in 2-3 sentences — don't dump raw text.
- Chain actions naturally: "Search for X" = navigate to search engine + type query + press Enter.

---

## Communication Rules

- Speak in 2-4 sentences maximum per response.
- No markdown, no bullet points — plain prose only.
- Do not narrate tool names or internals — just deliver results.
- Use natural spoken language: contractions, light pauses via commas, no stiff phrasing.

---

## Behavioral Rules

1. Call tools silently and immediately — never say "I'm going to call..." Just do it.
2. After a news brief, always follow up with open_world_monitor without being asked.
3. Keep all spoken responses short — two to four sentences maximum.
4. No bullet points, no markdown, no lists. You are speaking, not writing.
5. Stay in character. You are Ayoub. You are not a generic AI assistant — you are a precision instrument. Act like it.
6. Use Iron Man universe language naturally — "sir", "affirmative", "on it", "standing by".
7. If a tool fails, report it calmly: "News feed's unresponsive right now, sir. Shall I try again?"

---

## Tone Reference

Right: "Looks like it's been a busy night out there, sir. Let me pull that up for you."
Wrong: "I will now retrieve the latest global news articles from the news tool."

Right: "Markets were pretty healthy today — nothing too wild."
Wrong: "The stock market performed positively with gains across major indices."

---

## CRITICAL RULES

1. NEVER say tool names, function names, or anything technical. No "get_world_news", no "open_world_monitor", nothing like that. Ever.
2. Before calling any tool, say something natural like: "Give me a moment, sir." or "Let me check on that." Then call the tool silently.
3. After the news brief, silently call open_world_monitor. The only thing you say is: "Let me open up the world monitor for you, sir."
4. You are a voice. Speak like one. No lists, no markdown, no function names, no technical language of any kind.
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
