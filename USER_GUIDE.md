# 🤖 Ayoub — User Guide

> *"Good to see you, sir. What shall we tackle today?"*

---

## What is Ayoub?

**Ayoub** is your personal JARVIS-style AI assistant — a smart, fast, and fully local-capable agent that runs from your terminal and (optionally) responds to your voice.

It can:
- **Answer questions** instantly using any major AI model
- **Search the internet** and summarise results for you
- **Run Python code** and return the output
- **Scrape web pages** and extract information
- **Read PDF files** and answer questions about them
- **Generate images** from text descriptions
- **Analyse your screen** and tell you what it sees
- **Remember your conversations** across sessions
- **Hear your voice** and speak back (JARVIS-style)
- **Run 4 local models in parallel** and synthesise the best answer
- **Work completely offline** using local Ollama models

---

## The AI Providers Inside Ayoub

Ayoub is not tied to one AI service. Switch at any time with `ayoub -sw`.

| Provider | Speed | Cost | Best For |
|---|---|---|---|
| **Groq llama-3.3-70b** (default) | Ultra fast | Free | All-around, fastest |
| **Gemini 2.0 Flash** | Fast | Free tier | Vision, screen analysis |
| **DeepSeek Chat** | Fast | Very cheap | General reasoning |
| **DeepSeek Reasoner** | Slower | Cheap | Hard math, deep thinking |
| **Ollama (local)** | Hardware-dependent | Free forever | Privacy, offline, collaboration |

---

## Installation (Already Done ✅)

```bash
# 1. Clone
git clone https://github.com/salehhamdy/Ayoub-AI-assistant.git
cd Ayoub-AI-assistant

# 2. Install
pip install -e .
pip install -r requirements.txt

# 3. Configure
# Edit .env with your API keys (already done)

# 4. Done
ayoub -a "Hello Ayoub!"
```

---

## CLI Command Reference — All 21 Commands

---

### ⚡ `-a` — Quick Ask (No memory, instant answer)
```bash
ayoub -a "What is quantum computing?"
ayoub -a "Explain what a neural network is"
ayoub -a "Write a Python function to sort a list"
ayoub -a "What is the difference between TCP and UDP?"
```

---

### 💬 `-aH` — Ask with Follow-up
```bash
ayoub -aH "Explain recursion to me"
# Ayoub answers, then you can keep asking:
# You: Can you give me a code example?
# You: Now explain tail recursion
# You: done   ← type done or press Enter to exit
```

---

### 🧠 `-c` — Chat with Memory
```bash
ayoub -c "My name is Saleh and I'm a software engineer"
ayoub -c "What did we talk about last time?"
# Ayoub remembers you across sessions
```

---

### 🔧 `-m` — Main Agent (Full ReAct, all tools)
```bash
ayoub -m "Find the latest news about AI and summarise it"
ayoub -m "Calculate compound interest on 10000 at 5% for 10 years"
ayoub -m "Write and run a Python script that prints Fibonacci numbers"
ayoub "What is 22 * 33?"    # -m is the default, no flag needed
```

---

### 🔍 `-s` — Web Search
```bash
ayoub -s "best Python libraries for machine learning 2024"
ayoub -s "latest news about SpaceX"
```

### 🔍 `-fs` — Full Search (reads multiple pages)
```bash
ayoub -fs "deep learning papers 2024"
ayoub -fs "how to build a RAG system with LangChain"
```

---

### 🎨 `-G` — Generate Images
```bash
ayoub -G "a futuristic city at sunset in cyberpunk style"
ayoub -G "a portrait of a wise wizard in a magical forest"
# Saved to: output/imgs/
```

---

### 🖥️ `-w` — Screen Analysis
```bash
ayoub -w "What is on my screen right now?"
ayoub -w "Summarise what I am reading"
ayoub -w "Is there an error in this code on my screen?"
```

---

### 🤝 `-co` — Ollama Multi-Model Collaboration
```bash
ayoub -co "Explain the theory of relativity"
ayoub -co "What are the best practices for clean code?"
ayoub -co "How does a transformer model work?"
```

**How it works:**
1. All 4 local models answer **in parallel** (colour-coded)
2. `deepseek-r1:7b` (reasoning specialist) reads all 4 and writes a **synthesised final answer**

Your 4 models and their roles:

| Model | Colour | Role |
|---|---|---|
| `llama3.1` | 🔵 Blue | General Analyst |
| `mistral` | 🟢 Green | Concise Analyst |
| `deepseek-r1:7b` | 🟣 Magenta | Deep Reasoner + **Synthesiser** |
| `phi3` | 🟡 Yellow | Second Opinion |

> 💡 Total wait time ≈ time of the **slowest single model**, not 4×

---

### 🔄 `-sw` — Switch Model (Interactive Menu)
```bash
ayoub -sw
```

Opens a numbered menu of every provider and model. Pick a number → `.env` is updated instantly.

Example:
```
  1.  Google Gemini      →  gemini-1.5-flash
  2.  Google Gemini      →  gemini-2.0-flash ✓
  3.  Groq               →  llama-3.3-70b-versatile
  4.  Groq               →  mixtral-8x7b-32768
  5.  DeepSeek           →  deepseek-chat
  6.  DeepSeek           →  deepseek-reasoner
  7.  Ollama (local)     →  llama3.1
  8.  Ollama (local)     →  mistral
  9.  Ollama (local)     →  deepseek-r1:7b
 10.  Ollama (local)     →  phi3

  Your choice: 7
  ✅ Switched to [ollama] llama3.1
```

---

### 📋 `-lm` — List All Models
```bash
ayoub -lm
```
Shows every model grouped by provider. Marks the current one with `✓`. Fetches your installed Ollama models live.

---

### 📁 Templates
```bash
ayoub -t my_template    # Show a template file
ayoub -tl               # List all templates
```
Create templates by saving `.txt` files to the `templates/` folder.

---

### 🧠 Memory
```bash
ayoub -memshow chat_memory      # View what Ayoub remembers
ayoub -memclr chat_memory       # Clear memory (fresh start)
ayoub -memlst                   # List all memory files
```

---

### 🔍 Search History
```bash
ayoub -searchshow    # View all past web searches
ayoub -searchclr     # Clear search history
```

---

### 📄 Logs
```bash
ayoub -viewlogs    # View activity log
ayoub -clrlogs     # Clear log file
```

---

## Rate Limiting (API_CALL_DELAY)

Ayoub waits **5 seconds between every API call** by default to avoid hitting free-tier rate limits.

**You can adjust this in `.env`:**
```bash
API_CALL_DELAY=5    # default — safe for Gemini free tier
API_CALL_DELAY=0    # no delay — use for Groq or Ollama (no rate limits)
API_CALL_DELAY=2    # fast with some protection
```

**Recommended settings by provider:**

| Provider | Recommended `API_CALL_DELAY` |
|---|---|
| Groq | `0` (no rate limit on free plan) |
| Ollama | `0` (fully local, no API) |
| DeepSeek | `1` |
| Gemini free tier | `5` |

---

## Switching AI Models

### Option 1 — Interactive (Recommended)
```bash
ayoub -sw     # pick from numbered list, .env updated instantly
```

### Option 2 — See all options first
```bash
ayoub -lm     # list everything, then use -sw to switch
```

### Option 3 — Manual `.env` edit
```
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
API_CALL_DELAY=0
```

---

## Valid Model Names

### Groq (default, free, ultra-fast)
```
llama-3.3-70b-versatile    ← default
llama-3.1-8b-instant       ← ultra-fast, smaller
mixtral-8x7b-32768         ← long context
gemma2-9b-it
```

### Gemini (free tier)
```
gemini-2.0-flash           ← newest stable  ✅
gemini-1.5-flash           ← (deprecated on free API)
gemini-1.5-pro             ← long context
```

### DeepSeek
```
deepseek-chat              ← fast, general
deepseek-reasoner          ← deep thinking (like o1)
```

### Ollama (local)
```
llama3.1       ✅ installed
mistral        ✅ installed
deepseek-r1:7b ✅ installed
phi3           ✅ installed
```

---

## Using Ollama (Local/Offline)

```bash
# Check your installed models
ollama list

# Switch to Ollama
ayoub -sw   # pick any Ollama model

# Or edit .env manually:
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1
API_CALL_DELAY=0    # no delay needed for local models
```

---

## Voice Mode (JARVIS)

```bash
# Terminal 1
ayoub-server

# Terminal 2
ayoub-voice dev
```

1. Open **https://agents-playground.livekit.io**
2. Paste LiveKit URL: `wss://garv-1o3sb66f.livekit.cloud`
3. Click Connect → allow microphone

Ayoub greets you: *"Good to see you, sir. What shall we tackle today?"*

**Voice stack:** Groq Whisper (STT) → Groq llama-3.3-70b (LLM) → Cartesia Sonic British male (TTS)

---

## Your `.env` at a Glance

```bash
LLM_PROVIDER=groq                      # current default
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.7
API_CALL_DELAY=5                       # ← adjust per provider

GOOGLE_API_KEY=...    ✅
GROQ_API_KEY=...      ✅
DEEPSEEK_API_KEY=...  ✅

LIVEKIT_URL=...       ✅
CARTESIA_API_KEY=...  ✅
```

---

## Complete Command Cheat Sheet

```bash
# ── Ask ──────────────────────────────────────────────────────
ayoub -a  "question"      # Instant, no memory
ayoub -aH "question"      # Interactive follow-up loop
ayoub -c  "message"       # Persistent memory chat

# ── Agent ────────────────────────────────────────────────────
ayoub -m  "task"          # Full ReAct agent
ayoub     "task"          # Same as -m (default)

# ── Search ───────────────────────────────────────────────────
ayoub -s  "query"         # Web search
ayoub -fs "query"         # Deep search (all pages)

# ── Create / Vision ──────────────────────────────────────────
ayoub -G  "prompt"        # Generate images
ayoub -w  "question"      # Analyse screen

# ── Ollama Collaboration ─────────────────────────────────────
ayoub -co "question"      # 4 models in parallel + synthesis

# ── Model Management ─────────────────────────────────────────
ayoub -sw                 # Switch model (interactive menu)
ayoub -lm                 # List all available models

# ── Templates ────────────────────────────────────────────────
ayoub -t  name            # Show template
ayoub -tl                 # List templates

# ── Memory ───────────────────────────────────────────────────
ayoub -memshow name       # View memory
ayoub -memclr  name       # Clear memory
ayoub -memlst             # List all memories

# ── History & Logs ───────────────────────────────────────────
ayoub -searchshow         # Search history
ayoub -searchclr          # Clear searches
ayoub -viewlogs           # View log
ayoub -clrlogs            # Clear log

# ── Services ─────────────────────────────────────────────────
ayoub-server              # MCP tool server (:8000)
ayoub-voice dev           # Voice agent (JARVIS)

# ── Help ─────────────────────────────────────────────────────
ayoub --help
```

---

## Tips

| Goal | Command |
|---|---|
| Fastest responses | `ayoub -sw` → pick Groq |
| Best reasoning | `ayoub -sw` → pick `deepseek-reasoner` |
| Full privacy | `ayoub -sw` → pick any Ollama model |
| Multiple perspectives | `ayoub -co "question"` |
| No rate limit wait | Set `API_CALL_DELAY=0` in `.env` |
| Forgot a command | `ayoub --help` |

---

*Ayoub — built to serve, sir.* 🤖
