# 🤖 Ayoub — User Guide v2.0.0

> *"Good to see you, sir. What shall we tackle today?"*

---

## What is Ayoub?

**Ayoub** is your personal JARVIS-style AI assistant — a smart, fast, and fully local-capable agent that runs from your terminal. It features a beautiful interactive menu, multi-provider LLM support, persistent memory, web search, image generation, screen analysis, and multi-model collaboration.

### What Ayoub can do

- 🤖 **Answer questions** using any major AI model (Groq, Gemini, DeepSeek, OpenAI, Ollama)
- 🔍 **Search the internet** and summarise results in real-time
- 🧠 **Remember your conversations** across sessions with persistent memory
- 🖼️ **Generate images** from text using Pollinations.ai (free, no key)
- 👁️ **Analyse your screen** with 6 auto-detected vision modes
- 🤝 **Run 4 local models in parallel** and synthesise the best answer
- 🔧 **Use 10 built-in prompt templates** for common tasks
- 💻 **Work completely offline** using local Ollama models
- 🎨 **Two CLI modes**: Enhanced Interactive Menu or Classic flag-based CLI

---

## Starting Ayoub

Simply run:
```bash
ayoub
```

You'll see the ASCII banner and a **mode selector**:

```
  ┌───────────────────────────────────────────┐
  │           CHOOSE YOUR CLI MODE            │
  └───────────────────────────────────────────┘

  [1]  Enhanced Interactive Menu
       Guided numbered menu — best for exploration

  [2]  Classic CLI  (flag-based)
       Type flags directly, e.g.  -m "What is AI?"

  ▶  Enter 1 or 2:
```

### Mode 1 — Enhanced Interactive Menu (Recommended)

After choosing mode 1 you see the full service menu:

```
  [ 1]  Main Agent (ReAct)
  [ 2]  Stateless Q&A
  [ 3]  Human Feedback Mode
  [ 4]  Chat with Memory
  [ 5]  Quick Web Search
  [ 6]  Full Scrape Search
  [ 7]  Generate Images
  [ 8]  Analyze Screen
  [ 9]  Show Prompt Template
  [10]  List Templates
  [11]  Memory Management
  [12]  Search History
  [13]  System Logs
  [14]  Switch Model/Provider
  [15]  List Available Models
  [16]  Model Collaboration
  [17]  Usage Examples
  [18]  Exit
```

**You can enter:**
- A **number** (1–18)
- A **keyword** like `search`, `generate`, `chat`, `exit`
- `help` or `usage` to see the full command cheatsheet
- `exit`, `quit`, `q`, or `bye` to close

The menu stays open between tasks — Ayoub never closes until you ask it to.

### Mode 2 — Classic CLI (flag-based)

A persistent REPL prompt where you type flags directly:

```
  ayoub> -m "What is quantum computing?"
  ayoub> -s "latest AI news"
  ayoub> -G "a dragon in a cyberpunk city"
  ayoub> help        ← show all commands
  ayoub> examples    ← show usage cheatsheet
  ayoub> exit        ← close
```

---

## The AI Providers Inside Ayoub

Ayoub is not tied to one AI service. Switch at any time with `ayoub -sw`.

| Provider | Speed | Cost | Best For |
|---|---|---|---|
| **Groq llama-3.3-70b** (default) | Ultra fast | Free | All-around, fastest |
| **Gemini 3 Flash Preview** | Fast | Free tier | Vision, screen analysis |
| **DeepSeek Chat** | Fast | Very cheap | General reasoning |
| **DeepSeek Reasoner** | Slower | Cheap | Hard math, deep thinking |
| **OpenAI GPT-4o** | Fast | Paid | Best quality |
| **Ollama (local)** | Hardware-dependent | Free forever | Privacy, offline, collaboration |

---

## Command Reference — All 21 Commands

### ⚡ `-a` — Quick Ask (stateless, no memory)
```bash
ayoub -a "What is quantum computing?"
ayoub -a "Write a Python function to sort a list"
ayoub -a "Explain the difference between TCP and UDP"
```

---

### 💬 `-aH` — Ask with Follow-up
```bash
ayoub -aH "Explain recursion to me"
# Ayoub answers, then you keep asking:
# You: Can you give me a code example?
# You: Now explain tail recursion
# You: done  ← type done or press Enter to exit
```

---

### 🧠 `-c` — Chat with Memory
```bash
ayoub -c "My name is Saleh and I'm a software engineer"
ayoub -c "What did we talk about last time?"
# Ayoub remembers across sessions
```

---

### 🔧 `-m` — Main Agent (Full ReAct, all tools)
```bash
ayoub -m "Find the latest AI news and summarise it"
ayoub -m "Calculate compound interest on 10000 at 5% for 10 years"
ayoub -m "Write and run a Python script that prints Fibonacci numbers"
ayoub "What is 22 * 33?"    # -m is the default
```

---

### 🔍 `-s` — Quick Web Search
```bash
ayoub -s "best Python libraries for machine learning 2025"
ayoub -s "latest news about SpaceX"
```

### 🔍 `-fs` — Full Scrape Search
```bash
ayoub -fs "deep learning papers 2024"
ayoub -fs "how to build a RAG system with Python"
```

---

### 🎨 `-G` — Generate Images
```bash
ayoub -G "a futuristic city at sunset in cyberpunk style"
ayoub -G "a portrait of a wise wizard in a magical forest"
ayoub -G "photorealistic mountain landscape at golden hour"
# Saved to: output/imgs/
```

**Auto-style detection:**
| Keyword in prompt | Model used | Style |
|---|---|---|
| photo, realistic | `flux-realism` | Photographic |
| anime, manga | `flux-anime` | Anime |
| 3d, render | `flux-3d` | 3D CGI |
| painting, watercolor | `flux-cablyai` | Artistic |
| (default) | `flux` | High quality |

---

### 🖥️ `-w` — Screen Analysis
```bash
ayoub -w "What is on my screen right now?"
ayoub -w "Summarise what I am reading"
ayoub -w "Is there an error in this code on my screen?"
ayoub -w "Extract all text from my screen"
ayoub -w "Translate what is on my screen to English"
```

**Auto-detected modes:**
| Your question contains | Mode | What Ayoub does |
|---|---|---|
| code, script, function | `CODE` | Reviews code, finds bugs |
| error, crash, exception | `ERROR` | Root cause + fix |
| summarise, summary | `SUMMARISE` | Structured key points |
| translate, arabic, french | `TRANSLATE` | Full translation |
| read, extract, text | `OCR` | Extracts all visible text |
| *(anything else)* | `DESCRIBE` | Full visual description |

**Vision cascade (auto-fallback):**
1. Google Gemini 2.0 Flash (best quality)
2. Groq Llama 4 Scout 17B (if Gemini quota hit)
3. Groq Llama 4 Maverick (secondary fallback)

---

### 🤝 `-co` — Ollama Multi-Model Collaboration
```bash
ayoub -co "Explain the theory of relativity"
ayoub -co "What are the best practices for clean code?"
```

How it works:
1. All 4 local models answer **in parallel** (colour-coded)
2. `deepseek-r1:7b` reads all answers and writes a **synthesised final answer**

| Model | Colour | Role |
|---|---|---|
| `llama3.1` | 🔵 Blue | General Analyst |
| `mistral` | 🟢 Green | Concise Analyst |
| `deepseek-r1:7b` | 🟣 Magenta | Deep Reasoner + **Synthesiser** |
| `phi3` | 🟡 Yellow | Second Opinion |

> 💡 Total wait time ≈ time of the **slowest single model**, not 4×

---

### 🔄 `-sw` — Switch Model / Provider
```bash
ayoub -sw
```
Opens a numbered menu of every provider and model. Pick a number → `.env` updated instantly.

### 📋 `-lm` — List All Models
```bash
ayoub -lm
```
Shows every model grouped by provider with RPM info. Marks current with `✓`.

---

## Prompt Templates

10 built-in templates are ready to use:

```bash
ayoub -tl                # list all templates
ayoub -t summarize       # view a template
ayoub -t code_review
ayoub -t explain
ayoub -t research
ayoub -t translate
ayoub -t write_email
ayoub -t debug
ayoub -t brainstorm
ayoub -t plan
ayoub -t image_prompt
```

| Template | Use Case |
|---|---|
| `summarize` | Concise bullet-point summary |
| `code_review` | Bugs, security, performance review |
| `explain` | Concept explanation with analogies |
| `research` | Multi-source research with citations |
| `translate` | Cultural-aware translation |
| `write_email` | Professional email drafting |
| `debug` | Root cause + fix for errors |
| `brainstorm` | Idea generation with ratings |
| `plan` | Project planning with phases/risks |
| `image_prompt` | Optimised AI image generation prompts |

---

## Memory Management

```bash
ayoub -memshow chat_memory      # View what Ayoub remembers
ayoub -memclr chat_memory       # Clear a memory file (fresh start)
ayoub -memlst                   # List all memory files
```

---

## Search History & Logs

```bash
ayoub -searchshow    # View all past web searches
ayoub -searchclr     # Clear search history
ayoub -viewlogs      # View activity log
ayoub -clrlogs       # Clear log file
```

---

## Rate Limiting (`API_CALL_DELAY`)

Ayoub waits between API calls to avoid free-tier rate limits.

```bash
# In .env:
API_CALL_DELAY=5    # safe for Gemini free tier (default)
API_CALL_DELAY=0    # no delay — use for Groq or Ollama
API_CALL_DELAY=2    # balanced
```

| Provider | Recommended delay |
|---|---|
| Groq | `0` |
| Ollama | `0` |
| DeepSeek | `1` |
| Gemini free tier | `5` |

---

## Model Reference

### Groq (default, free, ultra-fast)
```
llama-3.3-70b-versatile    ← default
llama-3.1-8b-instant       ← ultra-fast, smaller
mixtral-8x7b-32768         ← long context
gemma2-9b-it
```

### Google Gemini
```
gemini-3-flash-preview     ← newest, recommended
gemini-2.5-flash
gemini-2.5-pro
gemini-2.0-flash
gemini-2.0-flash-lite      (30 RPM)
```

### DeepSeek
```
deepseek-chat              ← fast, general
deepseek-reasoner          ← deep thinking (like o1)
```

### Ollama (local, offline)
```
llama3.1
mistral
deepseek-r1:7b
phi3
```

---

## Your `.env` at a Glance

```bash
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.7
API_CALL_DELAY=0

GOOGLE_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

---

## Tips & Power User Tricks

| Goal | What to do |
|---|---|
| Fastest responses | `ayoub -sw` → pick Groq |
| Best reasoning | `ayoub -sw` → pick `deepseek-reasoner` |
| Full privacy | `ayoub -sw` → pick any Ollama model |
| Multiple perspectives | `ayoub -co "question"` |
| No rate limit wait | Set `API_CALL_DELAY=0` in `.env` |
| See all commands | Type `help` in the menu or run `ayoub --help` |
| Quick task without menu | `ayoub -a "question"` (one-shot, no menu) |
| Re-use a prompt structure | `ayoub -t template_name` then copy and fill `{{placeholders}}` |

---

*Ayoub — built to serve, sir.* 🤖
