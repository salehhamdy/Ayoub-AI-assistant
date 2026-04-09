# Ayoub-AI-assistant — Complete Implementation Plan

> **Project path:** `c:\Users\ASUS\Downloads\Garv\Ayoub-AI-assistant\`
> **Platforms:** Windows 10/11 & Linux (Ubuntu/Debian/Arch)
> **Python:** ≥ 3.11 | **Package manager:** `uv`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Cross-Platform Strategy](#3-cross-platform-strategy)
4. [Complete Project Structure](#4-complete-project-structure)
5. [File-by-File Specification](#5-file-by-file-specification)
6. [Provider Switching Reference](#6-provider-switching-reference)
7. [Complete Rename Map](#7-complete-rename-map)
8. [CLI Flags Reference](#8-cli-flags-reference)
9. [Verification Plan](#9-verification-plan)

---

## 1. Overview

**Ayoub-AI-assistant** is a brand-new project that fuses:

| Source Project | What it contributes |
|---|---|
| `friday-tony-stark-demo` | Voice pipeline (LiveKit + STT/TTS), FastMCP tool server, async news/fetch/system tools |
| `hereiz-AI-terminal-assistant` | ReAct reasoning loop, persistent memory, multi-mode CLI, screen analysis, PDF reader, Python executor, image generation |
| **New** | Unified LLM layer with **Ollama** support (local models), full **Windows + Linux** compatibility, Python-native cross-platform CLI |

**Key design principle:** The two source projects are **not modified**. This is a clean slate.

All `hereiz` branding → renamed to `ayoub` everywhere (command name, filenames, class names, prompts, logs, memory files).

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                     AYOUB-AI-ASSISTANT                               │
│                                                                      │
│  ┌──────────────────┐     ┌──────────────────┐                       │
│  │   CLI mode       │     │   Voice mode     │                       │
│  │  `ayoub` command │     │  `ayoub-voice`   │                       │
│  │  (Python-native, │     │  (LiveKit cloud) │                       │
│  │   Win + Linux)   │     │  [optional]      │                       │
│  └────────┬─────────┘     └────────┬─────────┘                       │
│           └─────────────┬──────────┘                                 │
│                         ▼                                            │
│              ┌───────────────────┐                                   │
│              │   LLM Layer       │ ◄── Provider factory              │
│              │   (build_llm())   │     gemini | openai               │
│              │                   │     groq   | ollama               │
│              └─────────┬─────────┘                                   │
│                        ▼                                             │
│              ┌───────────────────┐                                   │
│              │   ReAct Engine    │  Thought → Action → Observation   │
│              │   (agent/)        │  → Final Answer                   │
│              └─────┬────┬────────┘                                   │
│                    │    │                                            │
│         ┌──────────┘    └────────────┐                               │
│    ┌────▼──────┐              ┌──────▼───────────────────────────┐   │
│    │  Memory   │              │  ToolKit                         │   │
│    │  (files)  │              │  search | python | scrape | pdf  │   │
│    │  Win+Lin  │              │  news   | screen | image_gen     │   │
│    └───────────┘              └──────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  FastMCP Server  `ayoub-server`  (SSE on :8000)              │    │
│  │  Tools: get_world_news | search_web | fetch_url | system     │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Cross-Platform Strategy

### 3.1 CLI Entry Point — No Bash on Windows

**Problem:** The original `hereiz` is a bash script. Bash does not exist natively on Windows.

**Solution:** CLI is implemented as a **Python module** (`ayoub/cli.py`) registered as a `console_scripts` entry point:

```toml
[project.scripts]
ayoub        = "ayoub.cli:main"
ayoub-server = "ayoub.mcp_server.server:main"
ayoub-voice  = "ayoub.voice.agent:dev"
```

After `uv sync`, uv generates:
- **Windows:** `.venv\Scripts\ayoub.exe`
- **Linux:** `.venv/bin/ayoub`

Both callable simply as `ayoub` from terminal. No bash required.

### 3.2 Path Handling — pathlib.Path Everywhere

**Problem:** Windows uses `\`, Linux uses `/`.

**Solution:** `pathlib.Path` throughout ALL Python code — no raw `/` or `\` strings.

```python
from pathlib import Path
BASE_DIR   = Path(__file__).parent.parent.resolve()
DATA_DIR   = BASE_DIR / "data"
MEMORY_DIR = DATA_DIR / "memory"
LOG_FILE   = BASE_DIR / "logs" / "ayoub.log"
```

### 3.3 Screen Capture — Platform Detection

**Problem:** Original `hereiz_screen.sh` uses Linux-only tools: `scrot`, `xwininfo`, `xprop`, `xrandr`.

**Solution:** Single Python module `ayoub/screen_capture.py` with OS detection:

```python
import platform
from pathlib import Path
from PIL import ImageGrab
import subprocess, shutil

def capture_screen(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "screenshot.png"
    system = platform.system()

    if system == "Windows":
        # PIL.ImageGrab works natively on Windows with Pillow
        img = ImageGrab.grab()
        img.save(out)

    elif system == "Linux":
        if shutil.which("scrot"):
            # scrot is fastest on Linux with X11
            subprocess.run(["scrot", str(out)], check=True)
        else:
            # Fallback: PIL.ImageGrab (requires display / Xvfb)
            img = ImageGrab.grab()
            img.save(out)
    else:
        raise OSError(f"Screen capture not supported on {system}")

    return out
```

### 3.4 Subprocess — sys.executable, No Shell

**Problem:** `python3` may not exist on Windows; `bash -c` doesn't work on Windows.

**Solution:** Always use `sys.executable` and `shell=False`:

```python
import sys, subprocess
result = subprocess.run(
    [sys.executable, "-c", code],
    capture_output=True, text=True, timeout=30
)
```

### 3.5 Logging — Python logging Module

**Problem:** Original `log.sh` uses bash `echo >>`. Not portable.

**Solution:** Python `logging` with `RotatingFileHandler`:

```python
import logging
from logging.handlers import RotatingFileHandler
from ayoub.config import LOG_FILE

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        h = RotatingFileHandler(LOG_FILE, maxBytes=200*1024, backupCount=2)
        h.setFormatter(logging.Formatter(
            "%(asctime)s [%(name)s] [%(levelname)s] - %(message)s"
        ))
        logger.addHandler(h)
    return logger
```

### 3.6 Browser Opening — webbrowser Module

**Problem:** Original code uses `google-chrome` command on Linux — not on Windows.

**Solution:** `import webbrowser; webbrowser.open(url)` — detects the default browser on both platforms.

### 3.7 Setup Scripts — Dual Files

- `setup.sh` → Linux/macOS (bash)
- `setup.bat` → Windows (cmd/PowerShell)

Both do identical things: install uv → `uv sync` → create dirs → copy `.env.example`.

### 3.8 uv Package Manager

- **Windows:** `pip install uv` or `winget install astral-sh.uv`
- **Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh` or `pip install uv`

Works identically on both platforms.

### 3.9 Ollama On Both Platforms

- **Windows:** Download from https://ollama.com/download/windows (native installer)
- **Linux:** `curl -fsSL https://ollama.com/install.sh | sh`

The Python `ollama` package connects to `http://localhost:11434` — no differences.

### 3.10 sketch_window — Cross-Platform tkinter

The sketch window for `sketch2img` uses Python's built-in `tkinter` which works on both Windows and Linux (requires `python3-tk` on some Linux distros).

---

## 4. Complete Project Structure

```
Ayoub-AI-assistant/
│
├── ayoub/                          ← Main Python package
│   ├── __init__.py
│   ├── config.py                   ← All constants + pathlib.Path paths
│   ├── cli.py                      ← Cross-platform CLI (replaces bash hereiz)
│   ├── screen_capture.py           ← Win + Linux screenshot
│   ├── logger.py                   ← Python logging (replaces log.sh)
│   │
│   ├── llm/                        ← Unified LLM adapter layer (NEW)
│   │   ├── __init__.py             ← build_llm() factory
│   │   ├── base.py                 ← AbstractLLM interface
│   │   ├── gemini.py               ← Google Gemini adapter
│   │   ├── openai_llm.py           ← OpenAI adapter
│   │   ├── groq_llm.py             ← Groq adapter
│   │   └── ollama_llm.py           ← Ollama adapter (local models, NEW)
│   │
│   ├── agent/                      ← ReAct engine
│   │   ├── __init__.py
│   │   ├── base_llm.py             ← AgentLLM wrapping build_llm()
│   │   ├── base_prompt.py          ← BasePrompt, ReActPrompt
│   │   ├── base_runtime.py         ← BaseRuntime
│   │   ├── react_runtime.py        ← ReActRuntime (loop + parser)
│   │   ├── humanloop_runtime.py    ← HumanLoopRuntime (-aH mode)
│   │   └── toolkit.py              ← BaseTool, ToolKit
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   └── file_memory.py          ← read/write/clear/list memory files
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search_tool.py          ← DuckDuckGo web search
│   │   ├── python_exec_tool.py     ← Python code executor (cross-platform)
│   │   ├── scrape_tool.py          ← URL scraper (BeautifulSoup)
│   │   ├── pdf_tool.py             ← PDF reader (PyPDF2)
│   │   ├── image_gen_tool.py       ← txt2img + sketch2img via Gradio
│   │   ├── screen_tool.py          ← screenshot → wraps screen_capture.py
│   │   ├── web_tools.py            ← get_world_news, fetch_url, open_world_monitor
│   │   └── system_tools.py         ← get_current_time, get_system_info
│   │
│   ├── modules/                    ← High-level agent modes
│   │   ├── __init__.py
│   │   ├── ask_agent.py            ← AyoubAskAgent (stateless Q&A)
│   │   ├── chat_agent.py           ← AyoubChatAgent + memory loop
│   │   ├── main_agent.py           ← AyoubMainAgent (full ReAct + all tools)
│   │   ├── search_agent.py         ← AyoubSearchAgent (web search)
│   │   ├── generate_agent.py       ← AyoubGenerativeAIAgent (image gen)
│   │   ├── screen_agent.py         ← AyoubScreenAgent (vision)
│   │   └── memory_agent.py         ← AyoubMemoryAgent (standalone memory ops)
│   │
│   ├── mcp_server/                 ← FastMCP tool server (from friday)
│   │   ├── __init__.py
│   │   ├── server.py               ← FastMCP app, SSE on :8000
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── web.py              ← news, search_web, fetch_url, world_monitor
│   │       ├── system.py           ← get_current_time, get_system_info
│   │       └── utils.py            ← format_json, word_count
│   │
│   └── voice/                      ← LiveKit voice agent (optional)
│       ├── __init__.py
│       └── agent.py                ← AyoubVoiceAgent (JARVIS persona)
│
├── helpers/
│   ├── __init__.py
│   ├── image_utils.py              ← save_imgs, show_images_side_by_side
│   └── sketch_window.py            ← sketch_window() tkinter (Win + Linux)
│
├── templates/                      ← Prompt template .txt files
├── data/
│   ├── memory/                     ← *.txt memory files
│   ├── tmp/                        ← screenshots, temp files
│   └── search_history.txt
├── logs/
│   └── ayoub.log                   ← Rotating log (max 200KB, 2 backups)
├── output/
│   ├── imgs/                       ← txt2img outputs
│   └── sketches/                   ← sketch2img outputs
│
├── pyproject.toml
├── .env.example
├── .gitignore
├── setup.sh                        ← Linux setup
├── setup.bat                       ← Windows setup
└── README.md
```

---

## 5. File-by-File Specification

### 5.1 `pyproject.toml`

```toml
[project]
name = "ayoub-ai-assistant"
version = "1.0.0"
description = "Ayoub — JARVIS-style AI assistant with ReAct, voice, MCP tools, and Ollama"
readme = "README.md"
requires-python = ">=3.11"

dependencies = [
    "python-dotenv",
    "rich",
    "colorama",

    # LLM providers
    "google-generativeai>=0.7.0",
    "langchain-google-genai",
    "langchain>=0.3.0",
    "langchain-core",
    "langchain-experimental",
    "langchain-openai",
    "langchain-groq",
    "openai",
    "groq",
    "ollama",                         # local models

    # MCP server
    "fastmcp",
    "httpx",

    # Voice (optional)
    "livekit-agents[openai,silero]>=1.5.1",
    "livekit-plugins-google>=1.5.1",
    "livekit-plugins-sarvam",

    # Tools
    "beautifulsoup4",
    "lxml",
    "requests",
    "PyPDF2",
    "pillow",           # ImageGrab works on Windows + Linux
    "opencv-python",
    "gradio_client",
    "matplotlib",
]

[project.scripts]
ayoub        = "ayoub.cli:main"
ayoub-server = "ayoub.mcp_server.server:main"
ayoub-voice  = "ayoub.voice.agent:dev"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["ayoub"]
```

---

### 5.2 `ayoub/config.py`

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# LLM
LLM_PROVIDER    = os.getenv("LLM_PROVIDER", "gemini")   # gemini|openai|groq|ollama
LLM_MODEL       = os.getenv("LLM_MODEL", "gemini-2.5-flash")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# API Keys
GOOGLE_API_KEY  = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Voice (LiveKit)
LIVEKIT_URL        = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY    = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")
STT_PROVIDER       = os.getenv("STT_PROVIDER", "sarvam")   # sarvam|whisper
TTS_PROVIDER       = os.getenv("TTS_PROVIDER", "openai")   # openai|sarvam
SARVAM_API_KEY     = os.getenv("SARVAM_API_KEY", "")
MCP_SERVER_PORT    = int(os.getenv("MCP_SERVER_PORT", "8000"))

# Paths — all pathlib.Path, no raw / or \ separators
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
```

---

### 5.3 LLM Layer — `ayoub/llm/`

#### `base.py` — Abstract interface
```python
from abc import ABC, abstractmethod

class AbstractLLM(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str: ...
    @abstractmethod
    def stream(self, prompt: str): ...   # generator
```

#### `gemini.py`
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from ayoub.llm.base import AbstractLLM

class GeminiLLM(AbstractLLM):
    def __init__(self, api_key, model, temperature):
        self._chain = ChatGoogleGenerativeAI(
            google_api_key=api_key, model=model, temperature=temperature
        ) | StrOutputParser()

    def generate(self, prompt): return self._chain.invoke(prompt)
    def stream(self, prompt):   yield from self._chain.stream(prompt)
```

#### `openai_llm.py`
```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from ayoub.llm.base import AbstractLLM

class OpenAILLM(AbstractLLM):
    def __init__(self, api_key, model, temperature):
        self._chain = ChatOpenAI(api_key=api_key, model=model,
                                 temperature=temperature) | StrOutputParser()
    def generate(self, prompt): return self._chain.invoke(prompt)
    def stream(self, prompt):   yield from self._chain.stream(prompt)
```

#### `groq_llm.py`
```python
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from ayoub.llm.base import AbstractLLM

class GroqLLM(AbstractLLM):
    def __init__(self, api_key, model, temperature):
        self._chain = ChatGroq(api_key=api_key, model=model,
                               temperature=temperature) | StrOutputParser()
    def generate(self, prompt): return self._chain.invoke(prompt)
    def stream(self, prompt):   yield from self._chain.stream(prompt)
```

#### `ollama_llm.py` — Key new file (local models)
```python
"""
Ollama adapter — run any locally-installed model.

Install Ollama:
  Windows: https://ollama.com/download/windows
  Linux:   curl -fsSL https://ollama.com/install.sh | sh

Pull a model then set .env:
  ollama pull llama3
  LLM_PROVIDER=ollama
  LLM_MODEL=llama3
"""
import ollama as _ollama
from ayoub.llm.base import AbstractLLM

class OllamaLLM(AbstractLLM):
    def __init__(self, model: str, base_url="http://localhost:11434", temperature=0.7):
        self.model = model
        self.temperature = temperature
        self._client = _ollama.Client(host=base_url)

    def generate(self, prompt: str) -> str:
        return self._client.generate(
            model=self.model, prompt=prompt,
            options={"temperature": self.temperature}
        )["response"]

    def stream(self, prompt: str):
        for chunk in self._client.generate(
            model=self.model, prompt=prompt,
            options={"temperature": self.temperature}, stream=True
        ):
            yield chunk.get("response", "")
```

#### `__init__.py` — Factory
```python
from ayoub.config import (LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE,
                           GOOGLE_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, OLLAMA_BASE_URL)

def build_llm(provider=LLM_PROVIDER, model=LLM_MODEL, temperature=LLM_TEMPERATURE):
    if provider == "gemini":
        from ayoub.llm.gemini import GeminiLLM
        return GeminiLLM(GOOGLE_API_KEY, model, temperature)
    elif provider == "openai":
        from ayoub.llm.openai_llm import OpenAILLM
        return OpenAILLM(OPENAI_API_KEY, model, temperature)
    elif provider == "groq":
        from ayoub.llm.groq_llm import GroqLLM
        return GroqLLM(GROQ_API_KEY, model, temperature)
    elif provider == "ollama":
        from ayoub.llm.ollama_llm import OllamaLLM
        return OllamaLLM(model=model, base_url=OLLAMA_BASE_URL, temperature=temperature)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}. Use: gemini|openai|groq|ollama")
```

---

### 5.4 Agent Engine — `ayoub/agent/`

Rebuilt entirely from `customAgents/` — no external sub-repo dependency.

#### `toolkit.py`
- `BaseTool(description, tool_name)` → abstract `execute_func(*params)`
- `ToolKit(tools=[])` → `_register()`, `execute_tool(name, *params)`, `list_tools()`, `_format_instructions()`

#### `base_prompt.py`
- `BasePrompt(prompt_string, img=None)` → `.prompt` string, `.img`
- `ReActPrompt(question, example_workflow, prompt_string, history)` → fills REACT_TEMPLATE with Ayoub persona, `{history}`, `{tools_and_role}`, `{tool_names}`, `{question}` slots

#### `base_runtime.py`
- `BaseRuntime(llm, prompt, toolkit)`
- `step() -> str` — streams LLM tokens to terminal, returns full response
- `loop(n_steps=1) -> str`
- `reset()` — clears prompt + image

#### `react_runtime.py`
- `ReActRuntime(llm, prompt, toolkit)` extends BaseRuntime
- `loop(agent_max_steps=10, verbose_tools=False) -> str`
  - Injects tool names/instructions into prompt
  - Per iteration: call `step()` → parse → if `finish` → return Final Answer
  - Else: execute tool → append `Observation:` to prompt → next iteration
- `_parse_response(response) -> Dict` — parses `Thought/Action/Action Input/Final Answer`

#### `humanloop_runtime.py`
- `HumanLoopRuntime(llm, prompt)` extends BaseRuntime
- After each response, prints + prompts: `"Would you like to continue? (follow-up or 'done')":`
- Used by `-aH` mode

#### `base_llm.py`
- `AgentLLM(provider, model, temperature)` wraps `build_llm()`
- `generate_response(input, output_style) -> str` — streams with colorama
- `invoke_response(input) -> str` — non-streaming (for memory summarization)
- `multimodal_generate(prompt, img, stream)` — for screen/vision tasks via Gemini

---

### 5.5 Memory — `ayoub/memory/file_memory.py`

```python
from pathlib import Path
from ayoub.config import MEMORY_DIR

def read_memory(name: str) -> str:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    path = MEMORY_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8") if path.exists() else ""

def write_memory(name: str, content: str) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    (MEMORY_DIR / f"{name}.txt").write_text(content, encoding="utf-8")

def clear_memory(name: str) -> None:
    path = MEMORY_DIR / f"{name}.txt"
    if path.exists():
        path.unlink()
        print(f"Memory '{name}' cleared.")
    else:
        print(f"Memory '{name}' not found.")

def list_memories() -> list[str]:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    return [p.stem for p in MEMORY_DIR.glob("*.txt")]

def show_memory(name: str) -> str:
    content = read_memory(name)
    print(f"\n=== Memory: {name} ===\n{content}\n" if content
          else f"Memory '{name}' is empty.")
    return content
```

---

### 5.6 Tools — `ayoub/tools/`

#### `search_tool.py` — `AyoubSearchTool(BaseTool)`
- DuckDuckGo HTML scraping (`duckduckgo.com/html/?q=`)
- Rotates 16 user-agents to avoid blocks
- `execute_func(query) -> str`
- Saves search history to `data/search_history.txt` if path configured
- Cross-platform: pure Python `requests` + `BeautifulSoup`

#### `python_exec_tool.py` — `AyoubPythonExecTool(BaseTool)`
- Extracts code from markdown ` ```python ... ``` ` blocks
- Runs via `subprocess.run([sys.executable, "-c", code], ...)`
- Captures stdout + stderr, timeout=30s
- Cross-platform: `sys.executable` (never `python3`)

#### `scrape_tool.py` — `AyoubScrapeTool(BaseTool)`
- `execute_func(url) -> str`
- `requests.get()` + `BeautifulSoup(html, "lxml").get_text()`
- Returns up to `max_num_chars=10000` characters

#### `pdf_tool.py` — `AyoubPDFTool(BaseTool)`
- `execute_func(pdf_path) -> str`
- `PyPDF2.PdfReader(path)` → joins all page text

#### `image_gen_tool.py`
- `AyoubTxt2ImgTool` → Gradio `mukaist/DALLE-4k` → saves to `output/imgs/`
- `AyoubSketch2ImgTool` → opens `tkinter` sketch window → Gradio `gparmar-img2img-turbo-sketch` → saves to `output/sketches/`
- Both display results side-by-side with `matplotlib`

#### `screen_tool.py` — `AyoubScreenTool(BaseTool)`
- `execute_func() -> str` (returns path to screenshot)
- Calls `ayoub.screen_capture.capture_screen(TMP_DIR)`
- Windows: `PIL.ImageGrab.grab()`; Linux: `scrot` or `PIL.ImageGrab`

#### `web_tools.py`
- `get_world_news() -> str` — async parallel RSS fetch: BBC, CNBC, NYT, Al Jazeera
- `fetch_url(url) -> str` — raw text via `httpx` (4000 char limit)
- `open_world_monitor() -> str` — `webbrowser.open("https://worldmonitor.app/")` (cross-platform)

#### `system_tools.py`
- `get_current_time() -> str` — ISO 8601
- `get_system_info() -> dict` — OS, version, machine, processor, Python version

---

### 5.7 Agent Modules — `ayoub/modules/`

All prompts identify as **"Ayoub"**, all classes prefixed `Ayoub`.

#### `ask_agent.py`
- `AyoubAskAgent` — stateless Q&A, no memory, uses `HumanLoopRuntime`
- System prompt: friendly expert, "my name is Ayoub"
- `run_ask(question, with_feedback=False)` — entry function

#### `chat_agent.py`
- `AyoubChatAgent` — reads `chat_memory` file → injects as `{history}` → responds
- `AyoubMemoryAgent` — after each chat, rewrites memory with updated long-term + short-term sections
- `AyoubMemoryReflectionEnv` — orchestrates `[ChatAgent → MemoryAgent]`
- System prompt: friendly conversationalist, references long-term + short-term memory, "my name is Ayoub"
- `run_chat(question)` — entry function

#### `main_agent.py`
- `AyoubMainAgent(ReActRuntime)` — initialized with ALL tools:
  - `search_tool`, `python_tool`, `scrape_tool`, `readpdf_tool`
  - `image_to_text_tool`, `sketch_to_image_tool`
  - `get_world_news_tool`, `get_current_time_tool`
- `loop(agent_max_steps=10, verbose_tools=True)`
- `run_main(question)` — entry function

#### `search_agent.py`
- `AyoubSearchAgent(ReActRuntime)` — tools: `search_tool`, `python_tool`
- `run_search(query, full=False)` — `full=True` scrapes multiple links

#### `generate_agent.py`
- `AyoubGenerativeAIAgent(ReActRuntime)` — tools: `text_to_image_tool`, `sketch_to_image_tool`
- System prompt: "you are Ayoub, generate content and tell user where it was saved"
- `run_generate(prompt)` — entry function

#### `screen_agent.py`
- `AyoubScreenAgent` — multimodal (vision), uses Gemini vision API
- `AyoubScreenMemorySeqEnv` — pipeline:
  1. Run `capture_screen()` → get screenshot path
  2. Feed image + question to `AyoubScreenAgent`
  3. Update screen memory file via `AyoubMemoryAgent`
- `run_screen(question)` — entry function

#### `memory_agent.py`
- `AyoubMemoryAgent` — 1-step LLM call that rewrites memory file
- Standalone management functions: `show_memory(name)`, `clear_memory(name)`, `list_memories()`
- Memory structure: **Long-term** (persistent facts) + **Short-term** (current session)
- `run_memshow(name)`, `run_memclr(name)`, `run_memlst()` — entry functions

---

### 5.8 MCP Server — `ayoub/mcp_server/`

#### `server.py`
```python
from fastmcp import FastMCP
from ayoub.mcp_server.tools import web, system, utils

mcp = FastMCP("Ayoub MCP Server")
web.register(mcp)
system.register(mcp)
utils.register(mcp)

def main():
    mcp.run(transport="sse", port=8000)

if __name__ == "__main__":
    main()
```

#### `tools/web.py` — MCP tools (async, from friday)
| Tool | Description |
|---|---|
| `get_world_news()` | Parallel async BBC/CNBC/NYT/Al-Jazeera RSS fetch |
| `search_web(query)` | Web search (DuckDuckGo) |
| `fetch_url(url)` | Raw page text via httpx (4000 chars) |
| `open_world_monitor()` | Opens worldmonitor.app via `webbrowser.open()` |

#### `tools/system.py`
| Tool | Description |
|---|---|
| `get_current_time()` | Returns ISO 8601 datetime |
| `get_system_info()` | Returns OS, version, machine, Python version |

#### `tools/utils.py`
| Tool | Description |
|---|---|
| `format_json(data)` | Pretty-prints JSON |
| `word_count(text)` | Returns word count |

---

### 5.9 Voice Agent — `ayoub/voice/agent.py`

JARVIS-style persona replacing F.R.I.D.A.Y.:

```
STT: sarvam (saaras:v3) | whisper
LLM: gemini-2.5-flash   | openai:gpt-4o
TTS: openai (nova)      | sarvam (bulbul:v3)
VAD: silero
MCP: http://localhost:8000/sse
```

**JARVIS Personality (replaces FRIDAY prompt):**
- Calls user **"sir"** (not "boss")
- Greeting: *"Good to see you, sir. What shall we tackle today?"*
- 2-4 sentence max spoken responses
- No markdown, no lists, no technical language
- After news brief → silently calls `open_world_monitor`
- Tone: measured, intelligent, occasionally dry

**`AyoubVoiceAgent` class:**
- Extends `livekit.agents.voice.Agent`
- `mcp_servers=[MCPServerHTTP(url="http://localhost:8000/sse")]`
- `on_enter()` → JARVIS greeting
- `_build_stt()`, `_build_llm()`, `_build_tts()` → provider factories

**Entry points:**
- `main()` → `cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))`
- `dev()` → injects `dev` into `sys.argv`, calls `main()`

---

### 5.10 CLI Entry Point — `ayoub/cli.py`

Pure Python cross-platform CLI using `argparse` — replaces bash `hereiz` script entirely.

```python
"""
ayoub/cli.py — Cross-platform CLI for Ayoub-AI-assistant.
Registered as console_script 'ayoub' in pyproject.toml.

Windows: ayoub.exe (in .venv\Scripts\)
Linux:   ayoub    (in .venv/bin/)
"""
import argparse, sys
from ayoub.logger import get_logger

logger = get_logger("ayoub-cli")

def main():
    parser = argparse.ArgumentParser(
        prog="ayoub",
        description="Ayoub — JARVIS-style AI assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ayoub -a "What is quantum computing?"
  ayoub -aH "Explain recursion"
  ayoub -c "Let's continue our discussion"
  ayoub -m "Search for AI news and summarize"
  ayoub -s "best Python ML libraries"
  ayoub -fs "deep learning papers 2024"
  ayoub -G "a futuristic city at sunset"
  ayoub -w "What's on my screen?"
  ayoub -t my_template
  ayoub -tl
  ayoub -memshow chat_memory
  ayoub -memclr chat_memory
  ayoub -memlst
  ayoub -searchshow
  ayoub -searchclr
  ayoub -viewlogs
  ayoub -clrlogs

Default (no flag): runs -m (main ReAct agent)
        """
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-m", "--main",       metavar="QUESTION", help="Full ReAct agent (default)")
    group.add_argument("-a", "--ask",        metavar="QUESTION", help="Stateless Q&A (no memory)")
    group.add_argument("-aH",                metavar="QUESTION", dest="ask_feedback", help="Ask with human-in-the-loop")
    group.add_argument("-c", "--chat",       metavar="QUESTION", help="Chat with persistent memory")
    group.add_argument("-s", "--search",     metavar="QUERY",    help="Web search + summarize")
    group.add_argument("-fs", "--fullsearch",metavar="QUERY",    help="Full search (scrapes many links)")
    group.add_argument("-G", "--generate",   metavar="PROMPT",   help="Generate images via Gradio")
    group.add_argument("-w", "--screen",     metavar="QUESTION", help="Analyze current screen")
    group.add_argument("-t",                 metavar="NAME",     dest="template", help="Show a template")
    group.add_argument("-tl",                action="store_true", help="List all templates")
    group.add_argument("-memshow",           metavar="NAME",     help="Show a memory file")
    group.add_argument("-memclr",            metavar="NAME",     help="Clear a memory file")
    group.add_argument("-memlst",            action="store_true", help="List all memory files")
    group.add_argument("-searchshow",        action="store_true", help="Show search history")
    group.add_argument("-searchclr",         action="store_true", help="Clear search history")
    group.add_argument("-viewlogs",          action="store_true", help="View log file")
    group.add_argument("-clrlogs",           action="store_true", help="Clear log file")

    # Positional: default to -m if just a bare string is given
    parser.add_argument("query", nargs="?", help="Question (defaults to main agent)")

    args = parser.parse_args()

    # Dispatch to the correct agent module
    if args.main or (args.query and not any(vars(args).values())):
        from ayoub.modules.main_agent import run_main
        run_main(args.main or args.query)

    elif args.ask:
        from ayoub.modules.ask_agent import run_ask
        run_ask(args.ask, with_feedback=False)

    elif args.ask_feedback:
        from ayoub.modules.ask_agent import run_ask
        run_ask(args.ask_feedback, with_feedback=True)

    elif args.chat:
        from ayoub.modules.chat_agent import run_chat
        run_chat(args.chat)

    elif args.search:
        from ayoub.modules.search_agent import run_search
        run_search(args.search, full=False)

    elif args.fullsearch:
        from ayoub.modules.search_agent import run_search
        run_search(args.fullsearch, full=True)

    elif args.generate:
        from ayoub.modules.generate_agent import run_generate
        run_generate(args.generate)

    elif args.screen:
        from ayoub.modules.screen_agent import run_screen
        run_screen(args.screen)

    elif args.template:
        from ayoub.config import TEMPLATES_DIR
        path = TEMPLATES_DIR / f"{args.template}.txt"
        print(path.read_text(encoding="utf-8") if path.exists()
              else f"Template '{args.template}' not found.")

    elif args.tl:
        from ayoub.config import TEMPLATES_DIR
        files = list(TEMPLATES_DIR.glob("*.txt"))
        print("\n".join(f.stem for f in files) if files else "No templates found.")

    elif args.memshow:
        from ayoub.modules.memory_agent import run_memshow
        run_memshow(args.memshow)

    elif args.memclr:
        from ayoub.modules.memory_agent import run_memclr
        run_memclr(args.memclr)

    elif args.memlst:
        from ayoub.modules.memory_agent import run_memlst
        run_memlst()

    elif args.searchshow:
        from ayoub.config import SEARCH_HISTORY
        print(SEARCH_HISTORY.read_text(encoding="utf-8")
              if SEARCH_HISTORY.exists() else "No search history found.")

    elif args.searchclr:
        from ayoub.config import SEARCH_HISTORY
        if SEARCH_HISTORY.exists():
            SEARCH_HISTORY.write_text("", encoding="utf-8")
            print("Search history cleared.")
        else:
            print("No search history found.")

    elif args.viewlogs:
        from ayoub.config import LOG_FILE
        print(LOG_FILE.read_text(encoding="utf-8")
              if LOG_FILE.exists() else "No log file found.")

    elif args.clrlogs:
        from ayoub.config import LOG_FILE
        if LOG_FILE.exists():
            LOG_FILE.write_text("", encoding="utf-8")
            print("Log file cleared.")

    elif args.query:
        from ayoub.modules.main_agent import run_main
        run_main(args.query)

    else:
        parser.print_help()
```

---

### 5.11 Screen Capture — `ayoub/screen_capture.py`

```python
"""
Cross-platform screen capture.
Windows → PIL.ImageGrab.grab()
Linux   → scrot (if available) or PIL.ImageGrab
"""
import platform, shutil, subprocess
from pathlib import Path

def capture_screen(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "screenshot.png"
    system = platform.system()

    if system == "Windows":
        from PIL import ImageGrab
        ImageGrab.grab().save(str(out))

    elif system == "Linux":
        if shutil.which("scrot"):
            subprocess.run(["scrot", str(out)], check=True)
        else:
            from PIL import ImageGrab
            ImageGrab.grab().save(str(out))

    else:
        raise OSError(f"Screen capture not supported on {system}")

    return out
```

---

### 5.12 Logger — `ayoub/logger.py`

```python
import logging
from logging.handlers import RotatingFileHandler
from ayoub.config import LOG_FILE, LOGS_DIR

def get_logger(name: str) -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        h = RotatingFileHandler(str(LOG_FILE), maxBytes=200*1024, backupCount=2)
        h.setFormatter(logging.Formatter(
            "%(asctime)s [%(name)s] [%(levelname)s] - %(message)s"
        ))
        logger.addHandler(h)
    return logger
```

---

### 5.13 Helpers — `helpers/`

#### `helpers/image_utils.py`
```python
import shutil, matplotlib.pyplot as plt
from pathlib import Path

def save_imgs(img_dirs: list[str], dest_dir: str) -> list[str]:
    """Copy generated images from temp Gradio dirs to dest_dir."""
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    saved = []
    for src in img_dirs:
        dst = dest / Path(src).name
        shutil.copy2(src, dst)
        saved.append(str(dst))
    return saved

def show_images_side_by_side(saved_imgs_dir: str):
    """Display all images in a dir side by side using matplotlib."""
    imgs = list(Path(saved_imgs_dir).glob("*.png")) + list(Path(saved_imgs_dir).glob("*.jpg"))
    if not imgs:
        return
    fig, axes = plt.subplots(1, len(imgs), figsize=(5 * len(imgs), 5))
    if len(imgs) == 1:
        axes = [axes]
    for ax, img_path in zip(axes, imgs):
        ax.imshow(plt.imread(str(img_path)))
        ax.axis("off")
    plt.tight_layout()
    plt.show()
```

#### `helpers/sketch_window.py`
```python
"""
Cross-platform tkinter sketch window.
Works on Windows (built-in tkinter) and Linux (requires python3-tk).
"""
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageDraw
import tempfile
from pathlib import Path

def sketch_window() -> str:
    """Open a blank canvas, let user draw, return path to saved PNG."""
    root = tk.Tk()
    root.title("Ayoub Sketch — Draw then close window")
    canvas = Canvas(root, width=512, height=512, bg="white", cursor="crosshair")
    canvas.pack()

    image = Image.new("RGB", (512, 512), "white")
    draw = ImageDraw.Draw(image)

    def paint(event):
        x, y, r = event.x, event.y, 5
        canvas.create_oval(x-r, y-r, x+r, y+r, fill="black", outline="")
        draw.ellipse([x-r, y-r, x+r, y+r], fill="black")

    canvas.bind("<B1-Motion>", paint)
    root.mainloop()

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    image.save(tmp.name)
    return tmp.name
```

---

### 5.14 Setup Scripts

#### `setup.sh` — Linux
```bash
#!/bin/bash
set -e

echo "=== Ayoub AI Assistant — Linux Setup ==="

# Install uv if not present
if ! command -v uv &>/dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install all Python deps
uv sync

# Create required directories
mkdir -p data/memory data/tmp logs output/imgs output/sketches templates

# Copy env template
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env created — fill in your API keys."
fi

echo ""
echo "Setup complete! Activate venv and run:"
echo "  ayoub -a 'Your question'    (ask mode)"
echo "  ayoub -c 'Hello'            (chat with memory)"
echo "  ayoub -m 'Search AI news'   (full ReAct agent)"
echo "  ayoub-server                (start MCP server)"
echo "  ayoub-voice                 (start voice agent, optional)"
```

#### `setup.bat` — Windows
```bat
@echo off
echo === Ayoub AI Assistant - Windows Setup ===

:: Install uv if not present
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing uv...
    pip install uv
)

:: Install all Python deps
uv sync

:: Create required directories
if not exist "data\memory"   mkdir "data\memory"
if not exist "data\tmp"      mkdir "data\tmp"
if not exist "logs"          mkdir "logs"
if not exist "output\imgs"   mkdir "output\imgs"
if not exist "output\sketches" mkdir "output\sketches"
if not exist "templates"     mkdir "templates"

:: Copy env template
if not exist ".env" (
    copy ".env.example" ".env"
    echo .env created — fill in your API keys.
)

echo.
echo Setup complete! Run:
echo   ayoub -a "Your question"   (ask mode)
echo   ayoub -c "Hello"           (chat with memory)
echo   ayoub -m "Search AI news"  (full ReAct agent)
echo   ayoub-server               (start MCP server)
echo   ayoub-voice                (voice agent, optional)
```

---

### 5.15 `.env.example`

```env
# ── LLM Provider ────────────────────────────────────────────────────────────
# Options: gemini | openai | groq | ollama
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.7

# ── Google Gemini ────────────────────────────────────────────────────────────
GOOGLE_API_KEY=your-google-api-key
# Get from: https://aistudio.google.com

# ── OpenAI ───────────────────────────────────────────────────────────────────
OPENAI_API_KEY=sk-proj-...
# Get from: https://platform.openai.com/api-keys

# ── Groq ─────────────────────────────────────────────────────────────────────
GROQ_API_KEY=gsk_...
# Get from: https://console.groq.com

# ── Ollama (local models — no API key needed) ─────────────────────────────────
OLLAMA_BASE_URL=http://localhost:11434
# Install Ollama first, then pull a model:
#   Windows: https://ollama.com/download/windows
#   Linux:   curl -fsSL https://ollama.com/install.sh | sh
#   Then:    ollama pull llama3
# Then set:
#   LLM_PROVIDER=ollama
#   LLM_MODEL=llama3       (or mistral, phi3, gemma3, qwen2, deepseek-r1, etc.)

# ── Voice / LiveKit (optional — only needed for ayoub-voice) ─────────────────
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxx
STT_PROVIDER=sarvam        # sarvam | whisper
TTS_PROVIDER=openai        # openai | sarvam
SARVAM_API_KEY=sk_xxxxxxx
# Get LiveKit credentials: https://cloud.livekit.io
# Get Sarvam key:          https://dashboard.sarvam.ai

# ── MCP Server ────────────────────────────────────────────────────────────────
MCP_SERVER_PORT=8000
```

---

### 5.16 `README.md` (outline)

The README will document:
- Project overview and what makes it unique
- Architecture diagram
- Quick start (4 commands: clone → setup → set .env → ayoub -a "hello")
- CLI flags table (full, same as section 8 below)
- Provider switching table
- Voice mode setup
- Ollama setup guide
- MCP server tools list
- Memory system explanation

---

## 6. Provider Switching Reference

Switch by editing TWO lines in `.env`:

| `LLM_PROVIDER` | `LLM_MODEL` examples | API Key needed | Speed / Cost |
|---|---|---|---|
| `gemini` | `gemini-2.5-flash`, `gemini-1.5-pro` | `GOOGLE_API_KEY` | Fast / Free tier |
| `openai` | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` | `OPENAI_API_KEY` | Moderate / Paid |
| `groq` | `llama-3.3-70b-versatile`, `mixtral-8x7b-32768` | `GROQ_API_KEY` | Very fast / Free tier |
| `ollama` | `llama3`, `mistral`, `phi3`, `gemma3`, `qwen2`, `deepseek-r1` | *(none — local)* | Depends on hardware |

> **Ollama quick test:**
> ```
> ollama pull llama3
> # In .env:
> LLM_PROVIDER=ollama
> LLM_MODEL=llama3
> ayoub -a "Hello, Ayoub!"
> ```

---

## 7. Complete Rename Map

Every instance of `hereiz` → `ayoub`:

| Old (hereiz) | New (ayoub) |
|---|---|
| `hereiz` (CLI command) | `ayoub` |
| `hereiz_screen.sh` | `ayoub/screen_capture.py` (Python, cross-platform) |
| `log.sh` + `hereiz.logs` | `ayoub/logger.py` + `logs/ayoub.log` |
| `customAgents/` (external repo) | `ayoub/agent/` (built-in, no external dep) |
| `from customAgents.* import *` | `from ayoub.agent.* import *` |
| `from modules.X import ...` | `from ayoub.modules.X import ...` |
| Class `FridayAgent` | Class `AyoubVoiceAgent` |
| Package `friday/` | Package `ayoub/mcp_server/` |
| Script `friday = "server:main"` | Script `ayoub-server = "ayoub.mcp_server.server:main"` |
| Script `friday_voice = "agent_friday:dev"` | Script `ayoub-voice = "ayoub.voice.agent:dev"` |
| `F.R.I.D.A.Y.` persona | `Ayoub / JARVIS` persona |
| `"boss"` (greeting) | `"sir"` (JARVIS-style) |
| `"your name is Hereiz"` (all prompts) | `"your name is Ayoub"` |
| `"Hereiz:"` (prompt examples) | `"Ayoub:"` |
| `class MainLLM`, `ChatLLM`, etc. | `class AyoubMainLLM`, `AyoubChatLLM`, etc. |
| Memory file: `chat_memory.txt` | `chat_memory.txt` (same name, different dir) |
| `logs/hereiz.logs` | `logs/ayoub.log` |
| `scripts/run_ask.sh` → `python3 Ask/` | `ayoub/modules/ask_agent.py` (pure Python) |
| `google-chrome` (for opening URLs) | `webbrowser.open()` (cross-platform) |
| `python3` in scripts | `sys.executable` (cross-platform) |
| `bash ./scripts/run_*.sh` | Direct Python module calls from `cli.py` |

---

## 8. CLI Flags Reference

All flags work via `ayoub` on both Windows and Linux:

| Flag | Long form | Description | Memory? |
|---|---|---|---|
| `-m 'q'` | `--main 'q'` | Full ReAct agent — auto-selects tools *(default)* | ✅ Optional |
| `-a 'q'` | `--ask 'q'` | Stateless Q&A — no memory, no tools | ❌ |
| `-aH 'q'` | — | Ask + human-in-the-loop feedback | ❌ |
| `-c 'q'` | `--chat 'q'` | Memory-aware conversational chat | ✅ |
| `-s 'q'` | `--search 'q'` | Web search + summarize | ❌ |
| `-fs 'q'` | `--fullsearch 'q'` | Full search (scrapes many links) | ❌ |
| `-G 'p'` | `--generate 'p'` | Generate images via Gradio | ❌ |
| `-w 'q'` | `--screen 'q'` | Analyze current screen (screenshot + vision) | ✅ |
| `-t 'name'` | — | Show content of a template file | — |
| `-tl` | — | List all template files | — |
| `-memshow 'n'` | `--memory_show 'n'` | Print a memory file | — |
| `-memclr 'n'` | `--memory_clear 'n'` | Delete a memory file | — |
| `-memlst` | `--memory_list` | List all memory files | — |
| `-searchshow` | `--search_show` | Print search history | — |
| `-searchclr` | `--search_clear` | Clear search history | — |
| `-viewlogs` | — | Print `logs/ayoub.log` | — |
| `-clrlogs` | — | Clear `logs/ayoub.log` | — |

### Usage Examples

```bash
# Ask a one-off question (no memory)
ayoub -a "What is quantum computing?"

# Ask with human-in-the-loop feedback
ayoub -aH "Explain recursion to me"

# Chat with persistent memory
ayoub -c "Let's continue our discussion"

# Use the main smart agent (auto-selects tools)
ayoub -m "Find the latest news about AI and summarize it"
ayoub "What is 22 * 33?"   # -m is the default (bare string)

# Web search
ayoub -s "best Python libraries for ML"
ayoub -fs "deep learning papers 2024"   # Full search (scrapes many links)

# Generate images
ayoub -G "a futuristic city at sunset"

# Analyze your screen
ayoub -w "What's on my screen right now?"

# Template management
ayoub -t my_template          # Show a template
ayoub -tl                     # List all templates

# Memory management
ayoub -memshow chat_memory    # View memory file
ayoub -memclr chat_memory     # Clear memory file
ayoub -memlst                 # List all memory files

# Search history
ayoub -searchshow             # View search history
ayoub -searchclr              # Clear search history

# Logs
ayoub -viewlogs
ayoub -clrlogs
```

**Bare string (no flag)** → defaults to `-m` (main ReAct agent):
```
ayoub "What is 22 * 33?"     → same as ayoub -m "What is 22 * 33?"
```

---

## 9. Verification Plan

### Step 1 — Setup
```bash
# Linux
cd c/Users/ASUS/Downloads/Garv/Ayoub-AI-assistant
bash setup.sh

# Windows (cmd or PowerShell)
cd C:\Users\ASUS\Downloads\Garv\Ayoub-AI-assistant
setup.bat
```
**Expected:** uv installs all deps, directories created, `.env` copied.

### Step 2 — Basic Ask (Gemini)
```bash
# In .env: LLM_PROVIDER=gemini, GOOGLE_API_KEY=<your key>
ayoub -a "What is the capital of France?"
```
**Expected:** Streams "Paris..." with cyan colorization.

### Step 3 — Ollama Mode
```bash
ollama pull llama3
# In .env: LLM_PROVIDER=ollama, LLM_MODEL=llama3
ayoub -a "Explain quantum computing briefly"
```
**Expected:** Response from local Ollama llama3 model.

### Step 4 — Chat + Memory Persistence
```bash
ayoub -c "My name is Ayoub and I love Python"
ayoub -c "What is my name?"          # should recall from memory
ayoub -memshow chat_memory           # should show saved memory
```

### Step 5 — ReAct Main Agent
```bash
ayoub -m "Search for the latest AI news and summarize the top 3 stories"
```
**Expected:** ReAct loop visible in terminal, `search_tool` invoked, summary returned.

### Step 6 — MCP Server
```bash
ayoub-server
# In another terminal:
curl http://localhost:8000/   # should return FastMCP info
```

### Step 7 — Cross-Platform Screen Capture
```bash
ayoub -w "What application is currently open on my screen?"
```
**Expected:** Screenshot taken → sent to LLM → descriptive answer.
- **Windows:** `PIL.ImageGrab.grab()` used silently
- **Linux:** `scrot` or `PIL.ImageGrab` used

### Step 8 — Voice Agent (Optional)
```bash
# In .env: set LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
# Start MCP server first:
ayoub-server
# Then in another terminal:
ayoub-voice
# Connect at: https://agents-playground.livekit.io
```
**Expected:** JARVIS voice greeting: *"Good to see you, sir. What shall we tackle today?"*

### Step 9 — Windows-Specific Verification
```powershell
# From Windows PowerShell (no WSL)
where ayoub       # should show .venv\Scripts\ayoub.exe
ayoub --help      # should show all flags
ayoub -a "hello"  # should work without any bash
```

### Step 10 — Groq Speed Test
```bash
# In .env: LLM_PROVIDER=groq, LLM_MODEL=llama-3.3-70b-versatile, GROQ_API_KEY=<key>
ayoub -a "Summarize the theory of relativity in 3 sentences"
```
**Expected:** Very fast response from Groq inference.

---

*Generated: 2026-04-09 | Conversation: c4219ddf-de1a-43cd-a088-1587c82a90ec*
