# Ayoub AI Assistant — Project Progress Log

> **Last updated:** 2026-04-16  
> **Repo:** https://github.com/salehhamdy/Ayoub-AI-assistant  
> **Current version:** v2.0.0  
> **Default model:** `llama-3.3-70b-versatile` (Groq)

---

## Session Summary

This document tracks everything built, fixed, and enhanced in the Ayoub AI Assistant project across all development sessions.

---

## Phase 1 — Core CLI & Agent Architecture

### What was built
- Full CLI with 21 commands registered in `ayoub/cli.py`
- ReAct agent runtime (`react_runtime.py`) with multi-step tool loop
- Human-in-the-loop runtime (`humanloop_runtime.py`) for feedback
- Base LLM abstraction (`base_llm.py`) supporting multiple providers
- Memory system (`file_memory.py`) for persistent chat context
- Template system (`template_agent.py`) for reusable prompts

### CLI Commands Implemented
| Command | Description |
|---|---|
| `ayoub -a "..."` | Stateless ask (no memory) |
| `ayoub -aH "..."` | Ask with human-in-loop feedback |
| `ayoub -c "..."` | Chat with persistent memory |
| `ayoub -m "..."` | Full ReAct agent (all tools) — default |
| `ayoub -s "..."` | Web search agent |
| `ayoub -fs "..."` | Full search (scrapes multiple links) |
| `ayoub -G "..."` | Image generation |
| `ayoub -w "..."` | Screen analysis (vision) |
| `ayoub -t <name>` | Show a template |
| `ayoub -tl` | List all templates |
| `ayoub -memshow <name>` | View memory file |
| `ayoub -memclr <name>` | Clear memory file |
| `ayoub -memlst` | List all memory files |
| `ayoub -co "..."` | Multi-model Ollama collaboration |
| `ayoub -sw` | Interactive model switcher |
| `ayoub -lm` | List all available models |
| `ayoub -pdf <file>` | Read and analyse a PDF |
| `ayoub -py <file>` | Execute a Python file |
| `ayoub -mcp` | Start MCP server |
| `ayoub -voice` | Start voice mode (LiveKit) |
| `ayoub -ws` | Web scrape a URL |

---

## Phase 2 — Multi-Provider LLM Support

### Providers Added
| Provider | Key setting | Notes |
|---|---|---|
| Google Gemini | `GOOGLE_API_KEY` | Vision + embeddings |
| Groq | `GROQ_API_KEY` | Default speed provider |
| DeepSeek | `DEEPSEEK_API_KEY` | Reasoning models |
| OpenAI | `OPENAI_API_KEY` | GPT-4o family |
| Ollama | (local) | Offline, no key needed |

### Model Switcher (`ayoub -sw`)
- Interactive numbered menu persisted to `.env`
- Supports live switching without restarting
- Shows currently active model with `[*]`
- `ayoub -lm` shows full catalog with RPM info

### Ollama Collaboration (`ayoub -co`)
- Queries 4 local models **in parallel** via `ThreadPoolExecutor`
- Models: `llama3.1`, `mistral`, `deepseek-r1:7b`, `phi3`
- `deepseek-r1:7b` acts as synthesiser/judge
- Produces merged consensus answer

---

## Phase 3 — Search Engine Overhaul

### Problem
Old implementation scraped DuckDuckGo HTML → got bot-detected → returned 0 results or invalid redirect URLs.

### Fix
- Replaced with `ddgs` (official Python package, renamed from `duckduckgo_search`)
- Proper `DDGS()` API context manager — real search results
- URL decoder strips `?uddg=` redirect wrappers → real destination URLs
- Query cleaner strips LLM-generated inline notes before searching
- Removed all emoji from output → fixes Windows CP1252 encoding crash

### Result
```
[search_tool] Searching: 'latest AI news 2025'
[search_tool] >> AI News | Latest News  ->  https://www.artificialintelligence-news.com/
[Source: https://www.artificialintelligence-news.com/]
[Title: AI News | Latest News...]
SAP brings agentic AI to human capital management...
```

---

## Phase 4 — Rate Limiting & Stability

### API_CALL_DELAY
- Added `API_CALL_DELAY` config variable (default `5` seconds)
- Applied in `base_llm.py` before every `stream()` and `invoke_response()` call
- Prevents `429 RESOURCE_EXHAUSTED` on Gemini free tier
- Set to `0` for Groq/Ollama (no limits)

### ReAct Loop Fix
- Added hard `STOP` instruction after every real tool observation
- Prevents LLM from writing `"Assuming the observation is..."` (hallucinating results)
- Tool results are forced to `stdout` so LLM sees the actual observation

---

## Phase 5 — Gemini SDK Migration

### Problem
`google.generativeai` (legacy gRPC SDK) raised:
- `404 NOT_FOUND` on `gemini-1.5` models (removed from v1beta)
- `FutureWarning` about package being deprecated

### Fix
- Migrated to `google-genai` 1.x SDK (`from google import genai`)
- All Gemini calls now use `client.models.generate_content()`
- Vision calls migrated to same new SDK
- `gemini-2.0-flash` → `gemini-3-flash-preview` (from live model list)

---

## Phase 6 — New Gemini Models & Embedding

### Models discovered via `client.models.list()`
```
models/gemini-3-flash-preview      <- now default
models/gemini-2.5-flash
models/gemini-2.5-pro
models/gemini-2.0-flash
models/gemini-2.0-flash-lite       (30 RPM)
models/gemma-3-27b-it              (30 RPM)
models/gemma-3-12b-it
models/gemma-3-4b-it
models/gemini-embedding-001        (100 RPM)
models/gemini-embedding-2-preview
```

### GeminiEmbedder (`ayoub/llm/gemini_embed.py`)
Full embedding class using `gemini-embedding-001` (Gemini Embedding 1):
- `embed(text)` → 3072-dimension float vector
- `embed_bulk(texts)` → batch embedding
- `cosine_similarity(a, b)` → float similarity score
- `find_most_similar(query, candidates)` → ranked semantic search

**Live test results:**
```
Query: "machine learning algorithms"
  0.6848  deep learning       <- correctly ranked #1
  0.6521  neural networks     <- #2
  0.5907  quantum physics     <- #3
```

---

## Phase 7 — Image Generation Enhancement

### Old system
- Relied on Gradio spaces (mukaist/DALLE-4k) → frequently offline

### New system — Pollinations.ai (primary)
- **Free, no API key, always online**
- URL: `https://image.pollinations.ai/prompt/{prompt}`
- Auto-detects style from prompt keywords → picks best FLUX model

| Detected keyword | Model | Style |
|---|---|---|
| photo, realistic, portrait | `flux-realism` | Photographic |
| anime, manga, cartoon | `flux-anime` | Anime |
| 3d, render, blender | `flux-3d` | 3D CGI |
| painting, watercolor | `flux-cablyai` | Artistic |
| (default) | `flux` | High quality |

- Auto-enhances prompt with quality keywords per style
- Timestamps filenames: `ayoub_flux_20260414_162246.png`
- Auto-opens image after saving
- Gradio spaces kept as fallback

---

## Phase 8 — Screen Analysis Enhancement

### Old system
Single generic prompt → basic description

### New system — 6 auto-detected modes

| Question contains | Mode | What Ayoub does |
|---|---|---|
| code, script, function | `CODE` | Reviews code, finds bugs, suggests fixes |
| error, crash, exception | `ERROR` | Root cause + step-by-step fix |
| summarise, summary | `SUMMARISE` | Structured key points |
| translate, arabic, french | `TRANSLATE` | Full translation + cultural context |
| read, extract, text | `OCR` | Extracts all visible text |
| (anything else) | `DESCRIBE` | Full visual description |

- Coloured terminal output (`colorama`) with timestamp and mode indicator
- Screen memory saved with timestamp + mode label
- Structured, mode-specific prompt templates

---

## Phase 9 — Vision Provider Cascade

### Problem
`gemini-2.0-flash` free tier exhausted → vision returns 429 error

### Solution — Auto-cascade
```
1. Google Gemini gemini-2.0-flash    (best quality)
   ↓ if 429 quota error
2. Groq Llama 4 Scout 17B           (free, fast)  
   ↓ if model error
3. Groq Llama 4 Maverick 17B        (secondary fallback)
```

- `llama-3.2-90b-vision-preview` was decommissioned → replaced with Llama 4
- Vision cascade discovered via live terminal test (AI described VS Code screen accurately)

---

## Phase 10 — Requirements & Packaging

### Updated `requirements.txt`
```
ddgs>=9.0.0                    # search (renamed from duckduckgo-search)
google-genai>=1.0.0            # new unified Google SDK
google-generativeai>=0.8.0     # legacy (still needed for some calls)
groq>=0.10.0                   # Groq + vision
ollama>=0.5.0                  # local models
livekit-agents[silero]>=1.5.0  # voice (future)
livekit-plugins-groq>=1.5.0    # STT via Groq Whisper
livekit-plugins-cartesia>=1.5.0 # TTS via Cartesia
```

---

## Phase 11 — GitHub Achievements

### Actions taken
| Achievement | Action | Status |
|---|---|---|
| **Quickdraw** | Issue #1 opened + closed in <5 seconds | Earned |
| **Pull Shark** (Bronze) | PRs #2, #3, #4 merged (3 total) | Earned |
| **YOLO** | PRs merged without review on public repo | Processing |

- Installed GitHub CLI (`gh` v2.89.0)
- Authenticated as `salehhamdy`
- All feature branches merged and cleaned up

---

## Phase 12 — CLI Overhaul: Interactive Mode + Prompt Templates

### What was built

#### Mode Selector Splash
- Running `ayoub` with no arguments now shows a **mode selection screen** instead of jumping straight to the menu
- **Mode 1 — Enhanced Interactive Menu**: guided numbered menu, stays open between tasks
- **Mode 2 — Classic CLI**: persistent REPL where you type flags directly (e.g. `-m "What is AI?"`)
- Pressing Enter defaults to Mode 1

#### Enhanced Interactive Menu (18 items)
- Full numbered service menu with orange/green/blue colour scheme
- Sessions remain open — never closes until user exits
- **Case-insensitive, multi-input** support:
  - Numbers `1`–18
  - Label keywords: `search`, `generate`, `chat`, `screen`, etc.
  - Action names: `main`, `ask`, `tl`, `memlst`, etc.
  - Shortcuts: `exit`, `quit`, `q`, `bye` → clean exit
  - Help keywords: `help`, `?`, `usage`, `examples` → full cheatsheet
- Menu item 17 = **Usage Examples** (formatted cheatsheet with colours)
- Menu item 18 = Exit

#### Classic CLI Loop (`_classic_cli_loop`)
- Persistent `ayoub>` REPL — never need to re-run the command
- Accepts any flag: `-m`, `-s`, `-G`, `-co`, `-sw`, etc.
- Inline commands: `help`, `examples`, `exit`
- Full argparse parsing on each line via `shlex.split()`

#### ASCII Banner
- Orange `$$` AYOUB figlet banner printed on every launch
- Colour palette: Orange (banner/prompts), Blue (questions/menu borders), Green (answers/items)

#### Usage Cheatsheet (`_show_usage`)
- Available as menu option 17 and keyword `help`/`usage` in any mode
- Formatted table: Flag (green) | Description (blue) | Example (orange)
- Boxed header, separator lines, 21 commands covered

### Prompt Templates — 10 Built-in

New `templates/` directory populated with 10 ready-to-use `.txt` files:

| Template | Purpose |
|---|---|
| `summarize.txt` | Concise bullet-point summary |
| `code_review.txt` | Full code review: bugs, security, perf, style |
| `explain.txt` | Beginner-friendly concept explanation |
| `research.txt` | Multi-source research with citations |
| `translate.txt` | Cultural-aware translation |
| `write_email.txt` | Professional email drafting |
| `debug.txt` | Root cause + fix for code errors |
| `brainstorm.txt` | Idea generation with ratings |
| `plan.txt` | Project planning with phases/risks |
| `image_prompt.txt` | Optimised AI image generation prompts |

All use `{{placeholder}}` syntax. Accessible via `ayoub -t <name>` or menu option 9.

### Documentation Updated

| File | Change |
|---|---|
| `README.md` | Full v2.0.0 rewrite with mode selector, templates, all sections |
| `USER_GUIDE.md` | Complete rewrite covering both CLI modes, all 10 templates |
| `ENHANCEMENTS.md` | Full versioned changelog from v1.1 → v2.0.0 |
| `MANUAL.md` | New file — concise quick-reference card |
| `AYOUB_MANUAL.md` | New file — complete 17-section definitive manual |

### Git Commits (this session)
| Commit | Message |
|---|---|
| `3837741` | feat: interactive menu CLI with ASCII banner, colors, persistent session loop |
| `6775213` | feat: add SEE YOU ASCII goodbye banner on exit |
| `8df2588` | feat: remove SEE YOU goodbye banner, use simple farewell message |
| `7ca4807` | feat: add Usage Examples menu item with full CLI cheatsheet |
| `50e93e6` | feat: mode selector (Enhanced/Classic CLI), 10 prompt templates |
| `5a7a3d3` | feat: case-insensitive menu input + full README v2.0.0 rewrite |
| `f9915de` | docs: rewrite USER_GUIDE + ENHANCEMENTS, add MANUAL quick-reference |

---

## Current `.env` Configuration

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3-flash-preview
LLM_TEMPERATURE=0.7
API_CALL_DELAY=5
GOOGLE_API_KEY=<your key>
GROQ_API_KEY=<your key>
```

---

## What's Next — Voice Mode

The voice pipeline is already scaffolded in `requirements.txt`:

| Component | Provider | Package |
|---|---|---|
| **STT** (speech-to-text) | Groq Whisper | `livekit-plugins-groq` |
| **LLM** | Gemini / Groq | existing |
| **TTS** (text-to-speech) | Cartesia | `livekit-plugins-cartesia` |
| **VAD** (voice activity) | Silero (local) | `livekit-agents[silero]` |
| **Framework** | LiveKit Agents | `livekit-agents` |

**Files to build:**
- `ayoub/modules/voice_agent.py` — main voice loop
- `ayoub/voice/stt.py` — speech-to-text wrapper
- `ayoub/voice/tts.py` — text-to-speech wrapper
- CLI: `ayoub -voice` → already registered in `cli.py`

---

## File Structure (Key Files)

```
Ayoub-AI-assistant/
├── ayoub/
│   ├── cli.py                   # Enhanced + Classic interactive CLI (REWRITTEN)
│   ├── config.py                # Central config + AYOUB_VERSION
│   ├── logger.py                # Rotating logger
│   ├── screen_capture.py        # Screenshot utility
│   ├── agent/
│   │   ├── base_llm.py          # LLM abstraction + vision cascade
│   │   ├── base_runtime.py      # Base agent step loop
│   │   ├── react_runtime.py     # ReAct multi-step tool loop
│   │   ├── humanloop_runtime.py # Human feedback loop
│   │   ├── base_prompt.py       # Prompt templates
│   │   └── toolkit.py           # Tool registry
│   ├── llm/
│   │   ├── gemini.py            # Gemini provider (google-genai 1.x)
│   │   ├── gemini_embed.py      # GeminiEmbedder (3072-dim vectors)
│   │   ├── groq_llm.py          # Groq provider
│   │   ├── ollama_llm.py        # Ollama provider
│   │   └── __init__.py          # Provider factory
│   ├── modules/
│   │   ├── ask_agent.py         # -a / -aH
│   │   ├── chat_agent.py        # -c
│   │   ├── main_agent.py        # -m (default)
│   │   ├── search_agent.py      # -s / -fs
│   │   ├── generate_agent.py    # -G (Pollinations.ai)
│   │   ├── screen_agent.py      # -w (6 modes + cascade)
│   │   ├── memory_agent.py      # -mem*
│   │   ├── model_switcher.py    # -sw / -lm
│   │   └── ollama_collab.py     # -co (4-model parallel)
│   ├── tools/
│   │   ├── search_tool.py       # ddgs API (FIXED)
│   │   ├── image_gen_tool.py    # Pollinations.ai + FLUX (REWRITTEN)
│   │   ├── scrape_tool.py       # Web scraper
│   │   └── python_exec_tool.py  # Python executor
│   ├── memory/
│   │   └── file_memory.py       # Persistent memory
│   ├── mcp_server/          # FastMCP SSE tool server
│   └── voice/               # LiveKit JARVIS agent (scaffolded)
├── templates/               # 10 prompt templates (NEW)
│   ├── summarize.txt
│   ├── code_review.txt
│   ├── explain.txt
│   ├── research.txt
│   ├── translate.txt
│   ├── write_email.txt
│   ├── debug.txt
│   ├── brainstorm.txt
│   ├── plan.txt
│   └── image_prompt.txt
├── data/memory/             # Conversation memories
├── logs/ayoub.log           # Rotating log
├── output/imgs/             # Generated images
├── .env                     # Provider + model config
├── requirements.txt         # All dependencies
├── README.md                # GitHub landing page (REWRITTEN)
├── USER_GUIDE.md            # Detailed user guide (REWRITTEN)
├── MANUAL.md                # Quick reference card (NEW)
├── AYOUB_MANUAL.md          # Complete definitive manual (NEW)
├── ENHANCEMENTS.md          # Versioned changelog (REWRITTEN)
├── GEMINI_MODELS.md         # Model reference
└── progress.md              # This file
```
