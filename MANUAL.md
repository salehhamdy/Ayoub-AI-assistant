# Ayoub — Quick Reference Manual

> Version: v2.0.0 | Run `ayoub` to launch

---

## Launch

```bash
ayoub              # Interactive mode (shows mode selector)
ayoub -a "..."     # One-shot: skip menu, answer directly
```

---

## Mode Selector (shown on `ayoub` with no args)

```
[1]  Enhanced Interactive Menu   ← guided, numbered, stays open
[2]  Classic CLI (flag-based)    ← type flags like -m "..." directly
```

Press **Enter** to default to mode 1.

---

## Enhanced Menu — Accepted Inputs

| Input | Result |
|---|---|
| `1` – `18` | Select service by number |
| `search`, `chat`, `generate`… | Select by keyword |
| `exit` / `quit` / `q` / `bye` | Exit Ayoub |
| `help` / `usage` / `examples` / `?` | Show full cheatsheet |

---

## All CLI Flags

### Ask & Chat
| Flag | Description | Example |
|---|---|---|
| `-a "Q"` | Stateless Q&A (no memory) | `ayoub -a "What is AI?"` |
| `-aH "Q"` | Ask with follow-up loop | `ayoub -aH "Explain recursion"` |
| `-c "Q"` | Chat with persistent memory | `ayoub -c "Remember me"` |

### Agent
| Flag | Description | Example |
|---|---|---|
| `-m "Q"` | Full ReAct agent (default) | `ayoub -m "Latest AI news"` |
| `"Q"` | Same as `-m` (bare query) | `ayoub "What is 2+2?"` |

### Search
| Flag | Description | Example |
|---|---|---|
| `-s "Q"` | Quick web search | `ayoub -s "Python ML libs"` |
| `-fs "Q"` | Full scrape search | `ayoub -fs "LLM papers 2024"` |

### Vision & Generation
| Flag | Description | Example |
|---|---|---|
| `-G "P"` | Generate image | `ayoub -G "cyberpunk city"` |
| `-w "Q"` | Analyse screen | `ayoub -w "What's on screen?"` |

### Model Management
| Flag | Description |
|---|---|
| `-sw` | Interactive model/provider switcher |
| `-lm` | List all available models + RPM |
| `-co "Q"` | 4 Ollama models collaborate |

### Templates
| Flag | Description |
|---|---|
| `-t NAME` | Show a prompt template |
| `-tl` | List all templates |

### Memory
| Flag | Description |
|---|---|
| `-memshow NAME` | View a memory file |
| `-memclr NAME` | Delete a memory file |
| `-memlst` | List all memory files |

### History & Logs
| Flag | Description |
|---|---|
| `-searchshow` | Print search history |
| `-searchclr` | Clear search history |
| `-viewlogs` | Print log file |
| `-clrlogs` | Clear log file |

---

## Prompt Templates (10 built-in)

```bash
ayoub -tl                # list all
ayoub -t summarize       # structured summary
ayoub -t code_review     # bugs, security, perf
ayoub -t explain         # concept with analogy
ayoub -t research        # multi-source research
ayoub -t translate       # cultural translation
ayoub -t write_email     # professional email
ayoub -t debug           # root cause + fix
ayoub -t brainstorm      # ideas with ratings
ayoub -t plan            # project planning
ayoub -t image_prompt    # AI image prompt builder
```

---

## Providers & Models

| Provider | `.env` `LLM_PROVIDER` | Recommended model |
|---|---|---|
| Groq (default) | `groq` | `llama-3.3-70b-versatile` |
| Google Gemini | `gemini` | `gemini-3-flash-preview` |
| DeepSeek | `deepseek` | `deepseek-chat` |
| OpenAI | `openai` | `gpt-4o` |
| Ollama (local) | `ollama` | `llama3.1` |

Switch: `ayoub -sw`

---

## Key `.env` Settings

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.7
API_CALL_DELAY=0          # 0=Groq/Ollama, 5=Gemini free tier

GOOGLE_API_KEY=...
GROQ_API_KEY=...
DEEPSEEK_API_KEY=...
OPENAI_API_KEY=...
```

---

## Screen Analysis Modes (auto-detected from your question)

| Keyword in question | Mode | What happens |
|---|---|---|
| code, script, function | CODE | Code review + bug detection |
| error, crash, exception | ERROR | Root cause + fix |
| summarise, summary | SUMMARISE | Key bullet points |
| translate, arabic, french | TRANSLATE | Full translation |
| read, extract, text | OCR | Text extraction |
| *(anything else)* | DESCRIBE | Full visual description |

---

## Image Generation Auto-Style

| Keyword in prompt | FLUX model | Style |
|---|---|---|
| photo, realistic, portrait | `flux-realism` | Photographic |
| anime, manga, cartoon | `flux-anime` | Anime |
| 3d, render, blender | `flux-3d` | 3D CGI |
| painting, watercolor | `flux-cablyai` | Artistic |
| *(default)* | `flux` | High quality |

---

## Tips

| Goal | Action |
|---|---|
| Fastest answers | Switch to Groq, set `API_CALL_DELAY=0` |
| Best reasoning | Switch to `deepseek-reasoner` |
| Full privacy | Switch to any Ollama model |
| Multiple perspectives | `ayoub -co "question"` |
| Reuse a prompt | `ayoub -t template_name` → fill `{{placeholders}}` |
| See commands | Type `help` in Enhanced Menu |

---

*Full docs: `USER_GUIDE.md` | Change log: `ENHANCEMENTS.md` | Dev log: `progress.md`*
