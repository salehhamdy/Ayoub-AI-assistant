"""
ayoub/config.py — Central configuration for Ayoub-AI-assistant.
All file paths use pathlib.Path for Windows + Linux compatibility.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── LLM Provider ─────────────────────────────────────────────────────────────
# Options: "gemini" | "openai" | "groq" | "ollama"
LLM_PROVIDER    = os.getenv("LLM_PROVIDER", "groq")
LLM_MODEL       = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
API_CALL_DELAY  = float(os.getenv("API_CALL_DELAY", "5"))  # seconds between API calls)

# ── API Keys ──────────────────────────────────────────────────────────────────
GOOGLE_API_KEY  = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")

# ── DeepSeek (OpenAI-compatible) ─────────────────────────────────────────────
DEEPSEEK_API_KEY  = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# ── Ollama ────────────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ── Voice / LiveKit (optional) ────────────────────────────────────────────────
LIVEKIT_URL        = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY    = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")
STT_PROVIDER       = os.getenv("STT_PROVIDER", "sarvam")   # sarvam | whisper
TTS_PROVIDER       = os.getenv("TTS_PROVIDER", "openai")   # openai | sarvam
SARVAM_API_KEY     = os.getenv("SARVAM_API_KEY", "")
MCP_SERVER_PORT    = int(os.getenv("MCP_SERVER_PORT", "8000"))

# ── Paths (pathlib.Path — no hardcoded / or \ separators) ────────────────────
BASE_DIR        = Path(__file__).parent.parent.resolve()
DATA_DIR        = BASE_DIR / "data"
LOGS_DIR        = BASE_DIR / "logs"
TEMPLATES_DIR   = BASE_DIR / "templates"
OUTPUT_IMGS_DIR = BASE_DIR / "output" / "imgs"
OUTPUT_SKETCHES = BASE_DIR / "output" / "sketches"
MEMORY_DIR      = DATA_DIR / "memory"
TMP_DIR         = DATA_DIR / "tmp"
SEARCH_HISTORY  = DATA_DIR / "search_history.txt"
LOG_FILE        = LOGS_DIR / "ayoub.log"
