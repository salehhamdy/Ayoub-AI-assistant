# Ayoub AI Assistant — Enhancement Log

> Last updated: 2026-04-16 | Version: v2.0.0

---

## [v2.0.0] CLI Overhaul — Interactive Mode

### New Features
- **Mode Selector**: Running `ayoub` with no args now shows a mode-selection splash
  - Option 1: Enhanced Interactive Menu (guided numbered menu)
  - Option 2: Classic CLI (flag-based persistent REPL)
- **Enhanced Menu**: 18-item service menu, stays open between tasks
  - Accepts numbers (1–18), label keywords (e.g. `search`, `generate`), and shortcuts
  - Case-insensitive input — `EXIT`, `exit`, `q`, `bye` all work
  - `help` / `usage` / `examples` shows the full command cheatsheet
- **Classic CLI Loop**: Persistent REPL — type flags directly without restarting
  - `ayoub> -m "What is AI?"` — full ReAct agent
  - `ayoub> examples` — show usage cheatsheet
  - `ayoub> exit` — clean exit
- **ASCII Banner**: Orange AYOUB banner printed on every launch
- **Colour Scheme**: Orange = prompts/banner, Blue = questions, Green = answers/menu items
- **Usage Examples menu item** (option 17): Prints a full formatted CLI cheatsheet

---

## [v2.0.0] Prompt Templates — 10 Built-in Templates

New `templates/` directory with 10 ready-to-use prompt templates:

| File | Purpose |
|---|---|
| `summarize.txt` | Concise structured summary with bullet points |
| `code_review.txt` | Full code review: bugs, security, perf, style |
| `explain.txt` | Beginner-friendly concept explanation with analogies |
| `research.txt` | Multi-source research with citations |
| `translate.txt` | Cultural-aware language translation |
| `write_email.txt` | Professional email drafting |
| `debug.txt` | Root cause analysis + fix for code errors |
| `brainstorm.txt` | Idea generation with feasibility ratings |
| `plan.txt` | Project planning: phases, tasks, risks, metrics |
| `image_prompt.txt` | Optimised prompts for AI image generators |

Use with: `ayoub -t <template_name>` or menu option 9.

---

## [v1.9] Search Engine Overhaul

- Replaced broken HTML scraper with `ddgs` (official DuckDuckGo Python API)
- URL decoder strips `?uddg=` redirect wrappers → real destination URLs
- Query cleaner strips LLM-generated inline notes before searching
- Removed all emoji from output → fixes Windows CP1252 encoding crash

---

## [v1.8] Image Generation — Pollinations.ai

**Primary backend:** `https://image.pollinations.ai/prompt/{prompt}`
- Free, no API key, always online
- Auto-detects style from prompt keywords → picks best FLUX model

| Keyword | Model | Style |
|---|---|---|
| photo, realistic, portrait | `flux-realism` | Photographic |
| anime, manga, cartoon | `flux-anime` | Anime |
| 3d, render, blender | `flux-3d` | 3D CGI |
| painting, watercolor | `flux-cablyai` | Artistic |
| (default) | `flux` | High quality |

- Prompt auto-enhancement with model-specific quality keywords
- Timestamps filenames: `ayoub_flux_20260414_162246.png`
- Auto-opens image after saving
- Gradio spaces kept as fallback

---

## [v1.7] Screen Analysis — 6 Auto-detected Modes

| Question keyword | Mode | What Ayoub does |
|---|---|---|
| code, script, function | `CODE` | Reviews code, finds bugs, suggests fixes |
| error, crash, exception | `ERROR` | Root cause + step-by-step fix |
| summarise, summary | `SUMMARISE` | Structured key points |
| translate, arabic, french | `TRANSLATE` | Full translation + cultural context |
| read, extract, text | `OCR` | Extracts all visible text |
| (anything else) | `DESCRIBE` | Full visual description |

---

## [v1.6] Vision Provider Cascade

Auto-fallback chain when quota is exhausted:

```
1. Google Gemini 2.0 Flash       (best quality)
   ↓ if 429 quota error
2. Groq Llama 4 Scout 17B        (free, fast)
   ↓ if model error
3. Groq Llama 4 Maverick 17B     (secondary fallback)
```

---

## [v1.5] Gemini SDK Migration

- Migrated from deprecated `google.generativeai` → new `google-genai` 1.x SDK
- All Gemini calls now use `client.models.generate_content()`
- Default model updated: `gemini-2.0-flash` → `gemini-3-flash-preview`

---

## [v1.4] GeminiEmbedder

New `ayoub/llm/gemini_embed.py`:
- `embed(text)` → 3072-dimension float vector
- `embed_bulk(texts)` → batch embedding
- `cosine_similarity(a, b)` → float similarity score
- `find_most_similar(query, candidates)` → ranked semantic search

---

## [v1.3] Rate Limiting & Stability

- `API_CALL_DELAY` config variable (default `5` seconds)
- Applied before every `stream()` and `invoke_response()` call
- Prevents `429 RESOURCE_EXHAUSTED` on Gemini free tier
- ReAct loop fix: hard `STOP` instruction after every tool observation

---

## [v1.2] Multi-Provider LLM Support

| Provider | Key | Notes |
|---|---|---|
| Google Gemini | `GOOGLE_API_KEY` | Vision + embeddings |
| Groq | `GROQ_API_KEY` | Default speed provider |
| DeepSeek | `DEEPSEEK_API_KEY` | Reasoning models |
| OpenAI | `OPENAI_API_KEY` | GPT-4o family |
| Ollama | (local) | Offline, no key needed |

### Ollama Collaboration
- Queries 4 local models **in parallel** via `ThreadPoolExecutor`
- Models: `llama3.1`, `mistral`, `deepseek-r1:7b`, `phi3`
- `deepseek-r1:7b` acts as synthesiser/judge
- Total wait ≈ slowest single model (not 4×)

---

## [v1.1] Core CLI & Agent Architecture

- Full CLI with 21 commands registered in `ayoub/cli.py`
- ReAct agent runtime (`react_runtime.py`) with multi-step tool loop
- Human-in-the-loop runtime (`humanloop_runtime.py`) for feedback
- Base LLM abstraction (`base_llm.py`) supporting multiple providers
- Memory system (`file_memory.py`) for persistent chat context
- Template system for reusable prompts
