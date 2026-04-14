# Ayoub-AI-assistant

> **JARVIS-style AI assistant** — voice, ReAct agent, persistent memory, multi-model Ollama collaboration, and interactive model switching.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)](#)
[![GitHub](https://img.shields.io/badge/GitHub-Ayoub--AI--assistant-black)](https://github.com/salehhamdy/Ayoub-AI-assistant)

---

## What is Ayoub?

Ayoub merges the best of two worlds:

| Source | Contribution |
|---|---|
| `friday-tony-stark-demo` | Voice pipeline (LiveKit), FastMCP tool server, async news/web/system tools |
| `hereiz-AI-terminal-assistant` | ReAct reasoning loop, persistent memory, CLI, screen analysis, PDF reader, Python executor, image generation |
| **New** | Unified LLM layer (Gemini, Groq, DeepSeek, Ollama), model switcher, 4-model Ollama collaboration |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/salehhamdy/Ayoub-AI-assistant.git
cd Ayoub-AI-assistant

# 2. Install
pip install -e .
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env — add your API keys (Gemini key is enough to start)

# 4. Run
ayoub -a "Hello, Ayoub!"
```

---

## CLI Usage — All 21 Commands

```bash
# ── Ask ──────────────────────────────────────────────────────
ayoub -a "What is quantum computing?"      # Stateless Q&A
ayoub -aH "Explain recursion to me"        # Ask with follow-up feedback
ayoub -c "Let's continue our discussion"   # Chat with persistent memory

# ── Agent ────────────────────────────────────────────────────
ayoub -m "Find the latest AI news"         # Full ReAct agent (all tools)
ayoub "What is 22 * 33?"                   # -m is the default

# ── Search ───────────────────────────────────────────────────
ayoub -s "best Python libraries for ML"    # Web search
ayoub -fs "deep learning papers 2024"      # Full search (scrapes many links)

# ── Create / Vision ──────────────────────────────────────────
ayoub -G "a futuristic city at sunset"     # Generate images
ayoub -w "What's on my screen?"            # Screen analysis (vision)

# ── Ollama Multi-Model Collaboration ─────────────────────────
ayoub -co "Explain black holes"            # All 4 local models collaborate

# ── Model Management ─────────────────────────────────────────
ayoub -sw                                  # Interactive model switcher menu
ayoub -lm                                  # List all available models

# ── Templates ────────────────────────────────────────────────
ayoub -t my_template                       # Show a template
ayoub -tl                                  # List all templates

# ── Memory ───────────────────────────────────────────────────
ayoub -memshow chat_memory                 # View memory file
ayoub -memclr chat_memory                  # Clear memory file
ayoub -memlst                              # List all memory files

# ── History & Logs ───────────────────────────────────────────
ayoub -searchshow                          # View search history
ayoub -searchclr                           # Clear search history
ayoub -viewlogs                            # View log file
ayoub -clrlogs                             # Clear log file
```

---

## LLM Provider Switching

### Option A — Interactive Menu (Recommended)
```bash
ayoub -sw
```
Shows a numbered list of every provider and model. Pick a number → `.env` is updated instantly.

### Option B — List All Models
```bash
ayoub -lm
```
Shows all models grouped by provider, including your installed Ollama models.

### Option C — Manual `.env` edit

| `LLM_PROVIDER` | `LLM_MODEL` examples | API Key | Notes |
|---|---|---|---|
| `gemini` | `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash` | `GOOGLE_API_KEY` | Default, free tier |
| `groq` | `llama-3.3-70b-versatile`, `mixtral-8x7b-32768` | `GROQ_API_KEY` | Ultra-fast, free |
| `deepseek` | `deepseek-chat`, `deepseek-reasoner` | `DEEPSEEK_API_KEY` | Best reasoning |
| `ollama` | `llama3.1`, `mistral`, `phi3`, `deepseek-r1:7b` | *(none)* | Fully local, free |

---

## Ollama Multi-Model Collaboration

When you have multiple local models, Ayoub can run them **all in parallel** and synthesise the best answer:

```bash
ayoub -co "Explain the theory of relativity"
```

**How it works:**
1. All 4 models answer simultaneously in parallel (colour-coded output)
2. `deepseek-r1:7b` (the reasoner) reads all responses and writes a final unified answer

Your 4 models and their roles:

| Model | Role |
|---|---|
| `llama3.1` | General Analyst |
| `mistral` | Concise Analyst |
| `deepseek-r1:7b` | Deep Reasoner + Synthesiser |
| `phi3` | Second Opinion |

---

## Voice Agent (JARVIS)

```bash
ayoub-server        # Terminal 1 — MCP tool server
ayoub-voice dev     # Terminal 2 — voice agent
```

Connect at [agents-playground.livekit.io](https://agents-playground.livekit.io)

> *"Good to see you, sir. What shall we tackle today?"*

**Voice stack:** Groq Whisper (STT) → Groq llama-3.3-70b (LLM) → Cartesia Sonic British male (TTS)

---

## MCP Tool Server

```bash
ayoub-server   # Starts FastMCP server on :8000
```

Tools: `get_world_news`, `search_web`, `fetch_url`, `open_world_monitor`, `get_time`, `system_info`, `format_json`, `word_count`

---

## Project Structure

```
Ayoub-AI-assistant/
├── ayoub/
│   ├── config.py            ← All settings (pathlib.Path)
│   ├── cli.py               ← Cross-platform CLI (21 commands)
│   ├── llm/                 ← Gemini, OpenAI, Groq, DeepSeek, Ollama
│   ├── agent/               ← ReAct engine
│   ├── memory/              ← Persistent memory
│   ├── tools/               ← All 8 agent tools
│   ├── modules/
│   │   ├── ask_agent.py     ← -a / -aH
│   │   ├── chat_agent.py    ← -c
│   │   ├── main_agent.py    ← -m
│   │   ├── search_agent.py  ← -s / -fs
│   │   ├── generate_agent.py← -G
│   │   ├── screen_agent.py  ← -w
│   │   ├── memory_agent.py  ← -mem*
│   │   ├── model_switcher.py← -sw / -lm
│   │   └── ollama_collab.py ← -co
│   ├── mcp_server/          ← FastMCP SSE server
│   └── voice/               ← LiveKit JARVIS agent
├── helpers/
├── data/memory/             ← Conversation memories
├── logs/ayoub.log           ← Rotating log
├── output/imgs/             ← Generated images
├── templates/               ← Prompt templates
├── ollama_models.txt        ← Ollama download guide
├── USER_GUIDE.md            ← Full instruction manual
├── requirements.txt
└── .env.example
```

---

## Cross-Platform Notes

| Feature | Windows | Linux |
|---|---|---|
| CLI | `ayoub.exe` (pip-generated) | `ayoub` script |
| Screen capture | `PIL.ImageGrab` | `scrot` or `PIL.ImageGrab` |
| Model switcher | writes to `.env` directly | writes to `.env` directly |
| Sketch canvas | built-in tkinter | needs `python3-tk` |
