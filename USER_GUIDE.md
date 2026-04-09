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
- **Work completely offline** using local Ollama models

---

## The AI Providers Inside Ayoub

Ayoub is not tied to one AI service. You can switch at any time by editing two lines in `.env`:

| Provider | Speed | Cost | Best For |
|---|---|---|---|
| **Gemini 2.5 Flash** (default) | Fast | Free tier | General use, vision |
| **Groq llama-3.3-70b** | Ultra fast | Free | Quick answers |
| **DeepSeek Chat** | Fast | Very cheap | Reasoning tasks |
| **DeepSeek Reasoner** | Slower | Cheap | Complex thinking |
| **Ollama (local)** | Depends on GPU | Free forever | Privacy, offline use |

**To switch providers**, open `.env` and change:
```
LLM_PROVIDER=gemini       ← change to: groq, deepseek, or ollama
LLM_MODEL=gemini-2.5-flash ← change to match the provider
```

---

## Installation (Already Done ✅)

If you're reading this, setup is complete. But for reference:

```bash
# 1. Clone
git clone https://github.com/salehhamdy/Ayoub-AI-assistant.git
cd Ayoub-AI-assistant

# 2. Install
pip install -e .
pip install -r requirements.txt

# 3. Configure
# Edit .env with your API keys (already done)

# 4. Done — run your first command
ayoub -a "Hello Ayoub!"
```

---

## CLI Command Reference

### ⚡ Quick Ask — No memory, instant answer
```bash
ayoub -a "What is the speed of light?"
ayoub -a "Explain what a neural network is"
ayoub -a "Write a Python function to sort a list"
```

### 💬 Ask with Follow-up — Interactive back-and-forth
```bash
ayoub -aH "Explain quantum computing"
# Ayoub answers, then asks if you want to continue
# Type your follow-up, or press Enter / type 'done' to exit
```

### 🧠 Chat — Remembers your conversation history
```bash
ayoub -c "Hello, I'm working on a machine learning project"
ayoub -c "What libraries should I use?"
ayoub -c "Can you help me debug this error?"
# Each message remembers everything from before
```

### 🔧 Main Agent — Thinks and uses tools automatically
```bash
ayoub -m "Find the latest news about AI and summarise it"
ayoub -m "What is the weather like in Paris today?"
ayoub -m "Calculate the compound interest on 10000 at 5% for 3 years"
ayoub "What is 22 * 33?"   # -m is the default — no flag needed
```
Ayoub will automatically decide whether to search the web, run code, or answer directly.

### 🔍 Web Search
```bash
ayoub -s "best free AI tools 2024"        # Quick search
ayoub -fs "deep learning research papers"  # Full search (reads multiple pages)
```

### 🎨 Generate Images
```bash
ayoub -G "a futuristic city at sunset in cyberpunk style"
ayoub -G "a portrait of a wise wizard in a magical forest"
# Images saved to: output/imgs/
```

### 🖥️ Screen Analysis — Ayoub sees your screen
```bash
ayoub -w "What is on my screen?"
ayoub -w "Summarise what I am reading"
ayoub -w "Is there any error in this code on my screen?"
```

### 📁 Templates
```bash
ayoub -t my_template    # Show the content of a template file
ayoub -tl               # List all available templates
```
To create a template, save a `.txt` file to the `templates/` folder.

---

## Memory Management

Ayoub remembers conversations in text files inside `data/memory/`.

```bash
# View a memory file
ayoub -memshow chat_memory
ayoub -memshow screen_memory
ayoub -memshow main_memory

# Clear a memory file (start fresh)
ayoub -memclr chat_memory

# See all memory files
ayoub -memlst
```

---

## Search History

Every web search is logged to `data/search_history.txt`.

```bash
ayoub -searchshow    # View your search history
ayoub -searchclr     # Clear your search history
```

---

## Logs

All activity is logged to `logs/ayoub.log`.

```bash
ayoub -viewlogs    # View the log file
ayoub -clrlogs     # Clear the log file
```

---

## Using Local Models (Ollama — No Internet Needed)

Ollama lets Ayoub work completely offline and privately.

### Step 1 — Install Ollama
- **Windows:** https://ollama.com/download/windows
- **Linux:** `curl -fsSL https://ollama.com/install.sh | sh`

### Step 2 — Download a model
```bash
ollama pull llama3.1       # Best general model (4.7 GB)
ollama pull mistral        # Fast and efficient (4.1 GB)
ollama pull deepseek-r1:7b # Reasoning model (4.7 GB)
ollama pull phi3           # Small and fast (2.3 GB)
```
See `ollama_models.txt` for the full list.

### Step 3 — Switch Ayoub to Ollama
Open `.env` and set:
```
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1
```

### Step 4 — Run
```bash
ayoub -a "Hello, running locally!"
```

---

## Voice Mode (JARVIS)

Ayoub can listen to your voice and speak back like JARVIS from Iron Man.

### Requirements
- LiveKit account (already configured)
- Cartesia API key (already configured)
- Groq API key (already configured)

### Start Voice Mode
```bash
# Terminal 1 — Start the tool server
ayoub-server

# Terminal 2 — Start the voice agent
ayoub-voice dev
```

Then open **https://agents-playground.livekit.io**, paste your LiveKit URL, and connect.

Ayoub will greet you:
> *"Good to see you, sir. What shall we tackle today?"*

You can then speak naturally. Ayoub will transcribe your voice, think, and respond in a calm British male voice.

---

## MCP Tool Server

The MCP server exposes Ayoub's tools as a network API that the voice agent can use.

```bash
ayoub-server    # Starts on http://localhost:8000
```

Available tools via MCP:
- `get_world_news` — Fetch top world headlines
- `search_web` — Search the internet
- `fetch_url` — Read any URL
- `open_world_monitor` — Open global news monitor
- `get_time` — Current date and time
- `system_info` — OS and hardware info
- `format_json` — Pretty-print JSON
- `word_count` — Count words in text

---

## Switching Between AI Providers — Quick Reference

```bash
# Edit .env and change these two lines:

# Use Gemini (default, free tier)
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash

# Use Groq (fastest responses, free)
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile

# Use DeepSeek (great reasoning)
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
# or for deep thinking:
LLM_MODEL=deepseek-reasoner

# Use local Ollama (no internet, private)
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1
```

---

## File Structure

```
Ayoub-AI-assistant/
├── .env                  ← Your API keys and settings
├── requirements.txt      ← Python packages
├── ollama_models.txt     ← Ollama download guide
│
├── data/
│   ├── memory/           ← Conversation memories (chat_memory.txt, etc.)
│   └── search_history.txt ← Past searches
│
├── logs/
│   └── ayoub.log         ← Activity log
│
├── output/
│   └── imgs/             ← Generated images saved here
│
└── templates/            ← Custom prompt templates (.txt files)
```

---

## Tips & Tricks

| Goal | Command |
|---|---|
| Fastest responses | Set `LLM_PROVIDER=groq` |
| Best reasoning | Set `LLM_MODEL=deepseek-reasoner` |
| Full privacy | Set `LLM_PROVIDER=ollama` |
| Forget everything | `ayoub -memclr chat_memory` |
| See what Ayoub knows about you | `ayoub -memshow chat_memory` |
| Research a topic deeply | `ayoub -fs "your topic"` |
| Hands-free mode | Run `ayoub-server` then `ayoub-voice dev` |

---

## Need Help?

```bash
ayoub --help    # Full CLI reference
```

Or ask Ayoub himself:
```bash
ayoub -a "What can you do?"
```

---

*Ayoub — built to serve, sir.*
