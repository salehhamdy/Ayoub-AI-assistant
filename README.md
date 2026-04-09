# Ayoub-AI-assistant

> **JARVIS-style AI assistant** — blending voice, ReAct agent, persistent memory, and local Ollama models.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![uv](https://img.shields.io/badge/package_manager-uv-orange)](https://docs.astral.sh/uv/)
[![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)](#)

---

## What is Ayoub?

Ayoub merges the best of two worlds:

| Source | Contribution |
|---|---|
| `friday-tony-stark-demo` | Voice pipeline (LiveKit), FastMCP tool server, async news/web/system tools |
| `hereiz-AI-terminal-assistant` | ReAct reasoning loop, persistent memory, CLI, screen analysis, PDF reader, Python executor, image generation |
| **New** | Unified LLM layer supporting **Gemini, OpenAI, Groq, and local Ollama** models |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/salehhamdy/Ayoub-AI-assistant.git
cd Ayoub-AI-assistant

# 2. Setup
setup.bat       # Windows
bash setup.sh   # Linux

# 3. Configure
cp .env.example .env
# Edit .env — add your GOOGLE_API_KEY (or use Ollama for free)

# 4. Run
ayoub -a "Hello, Ayoub!"
```

---

## CLI Usage

```bash
ayoub -a "What is quantum computing?"      # Stateless Q&A
ayoub -aH "Explain recursion to me"        # Ask with follow-up feedback
ayoub -c "Let's continue our discussion"   # Chat with persistent memory
ayoub -m "Find the latest AI news"         # Full ReAct agent (all tools)
ayoub "What is 22 * 33?"                   # -m is the default
ayoub -s "best Python libraries for ML"    # Web search
ayoub -fs "deep learning papers 2024"      # Full search (scrapes many links)
ayoub -G "a futuristic city at sunset"     # Generate images
ayoub -w "What's on my screen?"            # Screen analysis (vision)
ayoub -t my_template                       # Show a template
ayoub -tl                                  # List all templates
ayoub -memshow chat_memory                 # View memory file
ayoub -memclr chat_memory                  # Clear memory file
ayoub -memlst                              # List all memory files
ayoub -searchshow                          # View search history
ayoub -searchclr                           # Clear search history
ayoub -viewlogs                            # View log file
ayoub -clrlogs                             # Clear log file
```

---

## LLM Provider Switching

Edit **two lines** in `.env`:

| `LLM_PROVIDER` | `LLM_MODEL` examples | API Key | Notes |
|---|---|---|---|
| `gemini` | `gemini-2.5-flash`, `gemini-1.5-pro` | `GOOGLE_API_KEY` | Default, free tier |
| `openai` | `gpt-4o`, `gpt-4o-mini` | `OPENAI_API_KEY` | Paid |
| `groq` | `llama-3.3-70b-versatile`, `mixtral-8x7b-32768` | `GROQ_API_KEY` | Very fast, free tier |
| `ollama` | `llama3`, `mistral`, `phi3`, `gemma3`, `qwen2`, `deepseek-r1` | *(none)* | Fully local |

### Using Ollama (local, free)

```bash
# Install: https://ollama.com
ollama pull llama3

# In .env:
LLM_PROVIDER=ollama
LLM_MODEL=llama3

ayoub -a "Hello!"
```

---

## MCP Tool Server

```bash
ayoub-server   # Starts FastMCP SSE server on :8000
```

Tools: `get_world_news`, `search_web`, `fetch_url`, `open_world_monitor`, `get_time`, `system_info`, `format_json`, `word_count`

---

## Voice Agent (Optional)

```bash
# Set in .env: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, SARVAM_API_KEY
ayoub-server   # Start MCP tools first
ayoub-voice    # Connect to LiveKit
```

Connect at [agents-playground.livekit.io](https://agents-playground.livekit.io)

> *"Good to see you, sir. What shall we tackle today?"*

---

## Project Structure

```
Ayoub-AI-assistant/
├── ayoub/
│   ├── config.py          ← All settings (pathlib.Path)
│   ├── cli.py             ← Cross-platform CLI
│   ├── logger.py          ← Rotating log
│   ├── screen_capture.py  ← Win: PIL / Linux: scrot
│   ├── llm/               ← Gemini, OpenAI, Groq, Ollama adapters
│   ├── agent/             ← ReAct engine
│   ├── memory/            ← Persistent memory
│   ├── tools/             ← All 8 agent tools
│   ├── modules/           ← ask, chat, main, search, generate, screen
│   ├── mcp_server/        ← FastMCP SSE server
│   └── voice/             ← LiveKit voice agent (JARVIS)
├── helpers/               ← Image utils, sketch window
├── setup.sh / setup.bat
├── pyproject.toml
└── .env.example
```

---

## Cross-Platform Notes

| Feature | Windows | Linux |
|---|---|---|
| CLI | `ayoub.exe` (uv-generated) | `ayoub` script |
| Screen capture | `PIL.ImageGrab` | `scrot` or `PIL.ImageGrab` |
| Browser open | `webbrowser.open()` | `webbrowser.open()` |
| Sketch canvas | built-in tkinter | needs `python3-tk` |
