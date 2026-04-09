# Ayoub-AI-assistant — Full Implementation Plan

## Background

This plan creates a **brand-new project** at:
```
c:\Users\ASUS\Downloads\Garv\Ayoub-AI-assistant\
```

It is a **complete fusion** of:
- **`friday-tony-stark-demo`** → voice pipeline (LiveKit), FastMCP tool server, async tools (news, web, system)
- **`hereiz-AI-terminal-assistant`** → ReAct agent loop, persistent memory, multi-mode CLI, screen analysis, PDF reader, Python executor, image generation

**All `hereiz` branding** → renamed to `ayoub` everywhere (CLI command, file names, class names, prompts, internal references).

**New addition**: Full Ollama support alongside Gemini, OpenAI, and Groq — single `.env` line to switch.

> [!IMPORTANT]
> The two existing projects (`friday-tony-stark-demo`, `hereiz-AI-terminal-assistant`) are **not modified**. This is a clean new project.

---

## Final Project Structure

```
Ayoub-AI-assistant/
│
├── ayoub                          ← main bash CLI entrypoint (replaces 'hereiz')
├── ayoub_screen.sh                ← screen capture helper (replaces hereiz_screen.sh)
├── setup.sh                       ← install script (uv sync + dir creation)
├── pyproject.toml                 ← uv-managed deps + CLI scripts
├── .env.example                   ← all env variables documented
├── .gitignore
├── README.md
│
├── ayoub/                         ← main Python package (replaces 'friday/' + root modules)
│   ├── __init__.py
│   ├── config.py                  ← all constants, provider flags, paths
│   │
│   ├── llm/                       ← unified LLM adapter layer (NEW)
│   │   ├── __init__.py
│   │   ├── base.py                ← AbstractLLM interface
│   │   ├── gemini.py              ← Google Gemini adapter
│   │   ├── openai_llm.py          ← OpenAI adapter
│   │   ├── groq_llm.py            ← Groq adapter
│   │   └── ollama_llm.py          ← Ollama adapter (NEW - local models)
│   │
│   ├── agent/                     ← ReAct engine (ported from customAgents)
│   │   ├── __init__.py
│   │   ├── base_llm.py            ← rebuilt BaseLLM using new llm/ layer
│   │   ├── base_runtime.py        ← BaseRuntime (ported from customAgents/runtime)
│   │   ├── react_runtime.py       ← ReActRuntime (ported from customAgents/runtime)
│   │   ├── humanloop_runtime.py   ← HumanLoopRuntime (for -aH mode)
│   │   ├── base_prompt.py         ← BasePrompt, ReActPrompt
│   │   └── toolkit.py             ← BaseTool, ToolKit classes
│   │
│   ├── memory/                    ← persistent memory system
│   │   ├── __init__.py
│   │   └── file_memory.py         ← read/write/clear memory files
│   │
│   ├── tools/                     ← all agent tools
│   │   ├── __init__.py
│   │   ├── search_tool.py         ← DuckDuckGo web search (from hereiz)
│   │   ├── python_exec_tool.py    ← Python runtime executor (from hereiz)
│   │   ├── scrape_tool.py         ← URL scraper with BeautifulSoup (from hereiz)
│   │   ├── pdf_tool.py            ← PDF reader via PyPDF2 (from hereiz)
│   │   ├── image_gen_tool.py      ← txt2img + sketch2img via Gradio (from hereiz)
│   │   ├── screen_tool.py         ← screenshot + vision analysis (from hereiz)
│   │   ├── web_tools.py           ← get_world_news, fetch_url (from friday)
│   │   └── system_tools.py        ← get_current_time, get_system_info (from friday)
│   │
│   ├── modules/                   ← high-level agent modes (replaces hereiz/modules/)
│   │   ├── __init__.py
│   │   ├── ask_agent.py           ← AskAgent (stateless Q&A, renamed from ask_agents.py)
│   │   ├── chat_agent.py          ← ChatAgent + MemoryReflectionEnv (from chat_agents.py)
│   │   ├── main_agent.py          ← MainAgent full ReAct (from main_agents.py)
│   │   ├── search_agent.py        ← SearchAgent (from search_agents.py)
│   │   ├── generate_agent.py      ← GenerativeAIAgent (from generate_agents.py)
│   │   ├── screen_agent.py        ← ScreenAgent + ScreenMemorySeqEnv (from screen_agents.py)
│   │   └── memory_agent.py        ← MemoryAgent standalone (from memory_agents.py)
│   │
│   ├── mcp_server/                ← FastMCP tool server (from friday)
│   │   ├── __init__.py
│   │   ├── server.py              ← FastMCP app, registers all tools, SSE on :8000
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── web.py             ← get_world_news, search_web, fetch_url, open_world_monitor
│   │   │   ├── system.py          ← get_current_time, get_system_info
│   │   │   └── utils.py           ← format_json, word_count
│   │
│   └── voice/                     ← LiveKit voice agent (from friday, optional)
│       ├── __init__.py
│       └── agent.py               ← AyoubVoiceAgent (replaces FridayAgent)
│
├── scripts/                       ← bash runner scripts (renamed from hereiz → ayoub)
│   ├── run_main.sh
│   ├── run_ask.sh
│   ├── run_askfeedback.sh
│   ├── run_chat.sh
│   ├── run_search.sh
│   ├── run_generate.sh
│   ├── run_screen.sh
│   ├── manage_logs.sh
│   ├── manage_memory.sh
│   ├── manage_search.sh
│   └── manage_templates.sh
│
├── templates/                     ← prompt template files (same as hereiz)
├── data/
│   └── tmp/                       ← screenshots, temp files
├── logs/
│   └── ayoub.log                  ← renamed from hereiz.log
├── helpers/
│   ├── __init__.py
│   ├── image_utils.py             ← save_imgs, show_images_side_by_side
│   └── sketch_window.py           ← sketch_window() helper
└── output/
    ├── imgs/                      ← generated images
    └── sketches/                  ← sketch-to-image outputs
```

---

## Proposed Changes — File by File

---

### `pyproject.toml` [NEW]

```toml
[project]
name = "ayoub-ai-assistant"
version = "1.0.0"
description = "Ayoub — JARVIS-style AI assistant blending voice, ReAct agent, MCP tools, and Ollama"
readme = "README.md"
requires-python = ">=3.11"

dependencies = [
    # Core
    "python-dotenv",
    "rich",
    "colorama",

    # LLM providers
    "google-generativeai>=0.7.0",
    "langchain-google-genai",
    "langchain",
    "langchain-core",
    "langchain-experimental",
    "langchain-openai",
    "openai",
    "groq",
    "ollama",                         # Ollama Python client

    # MCP server
    "fastmcp",
    "httpx",

    # Voice (optional — LiveKit)
    "livekit-agents[openai,silero]>=1.5.1",
    "livekit-plugins-google>=1.5.1",
    "livekit-plugins-sarvam",

    # Web / scraping tools
    "beautifulsoup4",
    "lxml",
    "requests",

    # File tools
    "PyPDF2",

    # Vision / screen tools
    "pillow",
    "opencv-python",

    # Image generation
    "gradio_client",
    "matplotlib",

    # Langchain parsers
    "langchain-core",
]

[project.scripts]
ayoub        = "ayoub.cli:main"           # CLI entrypoint
ayoub-server = "ayoub.mcp_server.server:main"  # MCP tool server
ayoub-voice  = "ayoub.voice.agent:dev"    # LiveKit voice agent

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["ayoub"]
```

---

### `ayoub/config.py` [NEW]

All configuration constants in one place:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM Provider ─────────────────────────────────────────────────────────────
# Options: "gemini" | "openai" | "groq" | "ollama"
LLM_PROVIDER     = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL        = os.getenv("LLM_MODEL", "gemini-2.5-flash")
LLM_TEMPERATURE  = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# ── API Keys ──────────────────────────────────────────────────────────────────
GOOGLE_API_KEY   = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")

# ── Ollama ────────────────────────────────────────────────────────────────────
OLLAMA_BASE_URL  = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# LLM_MODEL when LLM_PROVIDER=ollama, e.g.: llama3, mistral, phi3, gemma3, qwen2

# ── Voice (LiveKit) ───────────────────────────────────────────────────────────
LIVEKIT_URL        = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY    = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")

STT_PROVIDER     = os.getenv("STT_PROVIDER", "sarvam")     # sarvam | whisper
TTS_PROVIDER     = os.getenv("TTS_PROVIDER", "openai")     # openai | sarvam
SARVAM_API_KEY   = os.getenv("SARVAM_API_KEY", "")
MCP_SERVER_PORT  = int(os.getenv("MCP_SERVER_PORT", "8000"))

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR         = os.path.join(BASE_DIR, "data")
LOGS_DIR         = os.path.join(BASE_DIR, "logs")
TEMPLATES_DIR    = os.path.join(BASE_DIR, "templates")
OUTPUT_IMGS_DIR  = os.path.join(BASE_DIR, "output", "imgs")
OUTPUT_SKETCHES  = os.path.join(BASE_DIR, "output", "sketches")
MEMORY_DIR       = os.path.join(DATA_DIR, "memory")
TMP_DIR          = os.path.join(DATA_DIR, "tmp")
SEARCH_HISTORY   = os.path.join(DATA_DIR, "search_history.txt")
LOG_FILE         = os.path.join(LOGS_DIR, "ayoub.log")
```

---

### `ayoub/llm/` — Unified LLM Layer [NEW]

#### `ayoub/llm/base.py`

```python
from abc import ABC, abstractmethod

class AbstractLLM(ABC):
    """Universal interface that every provider adapter must implement."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response for the given prompt string."""
        ...

    @abstractmethod
    def stream(self, prompt: str):
        """Yield response tokens one at a time."""
        ...
```

#### `ayoub/llm/gemini.py`

Uses `langchain_google_genai.ChatGoogleGenerativeAI` with streaming via `chain.stream()`.
Exposes `generate(prompt) -> str` and `stream(prompt)` generator.

#### `ayoub/llm/openai_llm.py`

Uses `langchain_openai.ChatOpenAI`. Same interface.

#### `ayoub/llm/groq_llm.py`

Uses `langchain_groq.ChatGroq`. Same interface.

#### `ayoub/llm/ollama_llm.py` ← Key new file

```python
import ollama as _ollama
from ayoub.llm.base import AbstractLLM

class OllamaLLM(AbstractLLM):
    """
    Adapter for locally-running Ollama models.
    Requires Ollama installed: https://ollama.com
    Pull a model first: ollama pull llama3
    """
    def __init__(self, model: str, base_url: str = "http://localhost:11434",
                 temperature: float = 0.7):
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self._client = _ollama.Client(host=base_url)

    def generate(self, prompt: str) -> str:
        response = self._client.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temperature}
        )
        return response["response"]

    def stream(self, prompt: str):
        for chunk in self._client.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temperature},
            stream=True
        ):
            yield chunk.get("response", "")
```

#### `ayoub/llm/__init__.py`

```python
from ayoub.config import LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE
from ayoub.config import GOOGLE_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, OLLAMA_BASE_URL

def build_llm(
    provider: str = LLM_PROVIDER,
    model: str = LLM_MODEL,
    temperature: float = LLM_TEMPERATURE
):
    """Factory: returns the correct LLM adapter for the configured provider."""
    if provider == "gemini":
        from ayoub.llm.gemini import GeminiLLM
        return GeminiLLM(api_key=GOOGLE_API_KEY, model=model, temperature=temperature)
    elif provider == "openai":
        from ayoub.llm.openai_llm import OpenAILLM
        return OpenAILLM(api_key=OPENAI_API_KEY, model=model, temperature=temperature)
    elif provider == "groq":
        from ayoub.llm.groq_llm import GroqLLM
        return GroqLLM(api_key=GROQ_API_KEY, model=model, temperature=temperature)
    elif provider == "ollama":
        from ayoub.llm.ollama_llm import OllamaLLM
        return OllamaLLM(model=model, base_url=OLLAMA_BASE_URL, temperature=temperature)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}. "
                         "Valid: gemini | openai | groq | ollama")
```

---

### `ayoub/agent/` — ReAct Engine [PORTED + ENHANCED]

All classes are ported from `customAgents/` and fully renamed with `ayoub` branding throughout.

#### `ayoub/agent/toolkit.py`
- `BaseTool` class: `__init__(description, tool_name)`, abstract `execute_func(*params)`
- `ToolKit` class: `add_tool()`, `remove_tool()`, `execute_tool(name, *params)`, `list_tools()`, `_format_tool_instructions()`

#### `ayoub/agent/base_prompt.py`
- `BasePrompt(prompt_string, img=None)` — holds `.prompt` string and optional `.img`
- `ReActPrompt(question, example_workflow="", prompt_string="")` — fills in ReAct template with tool slots `{tool_names}`, `{tools_and_role}`, `{question}`

#### `ayoub/agent/base_llm.py`
- `AgentLLM(provider, model, temperature)` — wraps `build_llm()` from `ayoub.llm`
- `generate_response(input, output_style="cyan") -> str` — streams and colorizes output
- `invoke_response(input) -> str` — direct invoke (for memory summarization)
- `multimodal_generate(prompt, img, stream=True)` — for vision/screen tasks using Gemini vision

#### `ayoub/agent/base_runtime.py`
- `BaseRuntime(llm, prompt, toolkit)` — unchanged logic from hereiz
- `step(query=None) -> str`
- `loop(n_steps, query) -> str`
- `reset()`, `update_prompt()`, `add_to_prompt()`

#### `ayoub/agent/react_runtime.py`
- `ReActRuntime(llm, prompt, toolkit)` — unchanged logic from hereiz
- `loop(agent_max_steps=10, verbose_tools=False) -> str`
- `_parse_response(response) -> Dict[str, str]` — parses `Thought/Action/Action Input/Final Answer`

#### `ayoub/agent/humanloop_runtime.py`
- `HumanLoopRuntime(llm, prompt)` — for `-aH` flag: after each response, asks user if they want to continue

---

### `ayoub/memory/file_memory.py` [PORTED]

```python
import os
from ayoub.config import MEMORY_DIR

def read_memory(name: str) -> str:
    """Read memory file content. Returns empty string if file doesn't exist."""
    path = os.path.join(MEMORY_DIR, f"{name}.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return ""

def write_memory(name: str, content: str) -> None:
    """Write/overwrite memory file."""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(os.path.join(MEMORY_DIR, f"{name}.txt"), "w") as f:
        f.write(content)

def clear_memory(name: str) -> None:
    """Delete a memory file."""
    path = os.path.join(MEMORY_DIR, f"{name}.txt")
    if os.path.exists(path):
        os.remove(path)

def list_memory_files() -> list[str]:
    """Return all memory file names (without .txt extension)."""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    return [f.replace(".txt", "") for f in os.listdir(MEMORY_DIR) if f.endswith(".txt")]
```

---

### `ayoub/tools/` — All Agent Tools [PORTED + RENAMED]

#### `ayoub/tools/search_tool.py`
- Class: `AyoubSearchTool(BaseTool)`
- Inherits logic from `customAgents/agent_tools/search_tool.py`
- Uses DuckDuckGo HTML scraping (`duckduckgo.com/html/?q=`)
- Rotates user-agents to avoid blocks
- `execute_func(query: str) -> str` — returns scraped page text (up to `max_num_chars`)
- Optionally saves last search links to `data/search_history.txt`

#### `ayoub/tools/python_exec_tool.py`
- Class: `AyoubPythonExecTool(BaseTool)`
- Executes Python code blocks (extracts from markdown ` ```python ... ``` `)
- Captures `stdout` + `stderr` via `subprocess` with timeout
- Returns output string to the ReAct loop as observation

#### `ayoub/tools/scrape_tool.py`
- Class: `AyoubScrapeTool(BaseTool)`
- Uses `requests` + `BeautifulSoup` to scrape a URL
- Strips tags, returns up to `max_num_chars=10000` characters
- `execute_func(url: str) -> str`

#### `ayoub/tools/pdf_tool.py`
- Class: `AyoubPDFTool(BaseTool)`
- Uses `PyPDF2.PdfReader` to extract all page text
- `execute_func(pdf_path: str) -> str`

#### `ayoub/tools/image_gen_tool.py`
- Class: `AyoubTxt2ImgTool(BaseTool)` — calls Gradio `mukaist/DALLE-4k`
- Class: `AyoubSketch2ImgTool(BaseTool)` — opens sketch window, then calls `gparmar-img2img-turbo-sketch`
- Both save output to `output/imgs/` and `output/sketches/` respectively
- `execute_func(prompt: str) -> str`

#### `ayoub/tools/screen_tool.py`
- Class: `AyoubScreenTool`
- Runs `ayoub_screen.sh` to capture screenshot → saves to `data/tmp/`
- Returns image path for multimodal LLM consumption

#### `ayoub/tools/web_tools.py`
- `get_world_news()` — async, parallel fetch of BBC/CNBC/NYT/Al-Jazeera RSS feeds (from friday)
- `fetch_url(url: str) -> str` — raw text fetch via httpx
- `open_world_monitor() -> str` — opens `worldmonitor.app` in browser

#### `ayoub/tools/system_tools.py`
- `get_current_time() -> str` — ISO 8601 datetime
- `get_system_info() -> dict` — OS, version, machine, Python version

---

### `ayoub/modules/` — Agent Mode Implementations [RENAMED]

All `"Hereiz"` identity strings replaced with `"Ayoub"` in every system prompt.
All class names prefixed with `Ayoub`.

#### `ayoub/modules/ask_agent.py`
- `AyoubAskLLM(AgentLLM)` — `llm_generate(input) -> str` with cyan output
- `AyoubAskPrompt(BasePrompt)` — system prompt:
  > *"You are Ayoub, a helpful assistant expert in programming, ML, science, and math. Your name is Ayoub."*
- `AyoubAskAgent(HumanLoopRuntime)` — stateless Q&A, no memory
- Entry function: `run_ask(question: str, with_feedback: bool = False)`

#### `ayoub/modules/chat_agent.py`
- `AyoubChatLLM(AgentLLM)` — cyan output
- `AyoubChatPrompt(BasePrompt)` — system prompt with long-term + short-term `{history}` slot, identifies as Ayoub:
  > *"You are Ayoub, a friendly AI assistant. You remember the user's preferences and past interactions..."*
- `AyoubChatAgent(BaseRuntime)` — uses persistent `chat_memory` file
- `AyoubMemoryAgent` — runs after every chat, rewrites memory file with updated long-term + short-term sections
- `AyoubMemoryReflectionEnv(BaseEnv)` — orchestrates `[ChatAgent → MemoryAgent]` pipeline
- Entry function: `run_chat(question: str)`

#### `ayoub/modules/main_agent.py`
- `AyoubMainLLM(AgentLLM)` — green output
- `AyoubMainPrompt(ReActPrompt)` — full ReAct system prompt:
  > *"You are Ayoub, a friendly and helpful AI assistant. You have access to various tools..."*
  - Includes `{history}` slot for memory context
  - Includes full ReAct example workflow (search + python executor examples)
  - Tool slots: `{tools_and_role}`, `{tool_names}`
- `AyoubMainAgent(ReActRuntime)` — initialized with all tools:
  - `search_tool`, `python_tool`, `scrape_tool`, `readpdf_tool`, `image_to_text_tool`, `sketch_to_image_tool`, `get_world_news_tool`, `get_current_time_tool`
  - `loop(agent_max_steps=10, verbose_tools=True) -> str`
- Entry function: `run_main(question: str)`

#### `ayoub/modules/search_agent.py`
- `AyoubSearchLLM(AgentLLM)` — green output
- `AyoubSearchPrompt(ReActPrompt)` — focused search ReAct prompt
- `AyoubSearchAgent(ReActRuntime)` — tools: `search_tool`, `python_tool`
- Entry: `run_search(query: str, full: bool = False)` — `full=True` scrapes multiple links

#### `ayoub/modules/generate_agent.py`
- `AyoubGenerativeAILLM(AgentLLM)`
- `AyoubGenerativeAIPrompt(ReActPrompt)` — identifies as Ayoub:
  > *"Your name is Ayoub and you are an AI assistant. After generating content, tell the user where it was saved."*
- `AyoubGenerativeAIAgent(ReActRuntime)` — tools: `text_to_image_tool`, `sketch_to_image_tool`
- Entry: `run_generate(prompt: str)`

#### `ayoub/modules/screen_agent.py`
- `AyoubScreenLMM(AgentLLM)` — multimodal (vision), visualoutput style
- `AyoubScreenPrompt(BasePrompt)` — vision prompt with memory context:
  > *"You are Ayoub. You can see the user's screen. The terminal shows conversation history..."*
- `AyoubScreenAgent(BaseRuntime)` — multimodal loop
- `AyoubScreenMemorySeqEnv(BaseEnv)` — pipeline: `[capture_screenshot → ScreenAgent → MemoryAgent]`
  - Runs `ayoub_screen.sh` to capture screenshot
  - Feeds image to LLM
  - Updates screen memory file after each interaction
- Entry: `run_screen(question: str)`

#### `ayoub/modules/memory_agent.py`
- `AyoubMemoryLLM(AgentLLM)` — invoked for summarization (no streaming needed)
- `AyoubMemoryPrompt(BasePrompt)` — prompt for distilling long-term + short-term memory from conversation
- `AyoubMemoryAgent(BaseRuntime)` — 1 step, used internally by `ChatAgent` and `ScreenAgent`
- Standalone entries: `show_memory(name)`, `clear_memory(name)`, `list_memories()`

---

### `ayoub/mcp_server/` — FastMCP Tool Server [PORTED FROM FRIDAY]

#### `ayoub/mcp_server/server.py`

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

#### `ayoub/mcp_server/tools/web.py`
Exact port from `friday/tools/web.py`:
- `get_world_news()` — parallel async BBC/CNBC/NYT/Al-Jazeera RSS fetch
- `search_web(query: str)` — DuckDuckGo search
- `fetch_url(url: str)` — raw URL fetch via httpx (4000 char limit)
- `open_world_monitor()` — opens `worldmonitor.app` in browser

#### `ayoub/mcp_server/tools/system.py`
Exact port from `friday/tools/system.py`:
- `get_current_time()` — ISO datetime
- `get_system_info()` — OS, version, machine

#### `ayoub/mcp_server/tools/utils.py`
- `format_json(data)` — pretty format
- `word_count(text)` — returns word count

---

### `ayoub/voice/agent.py` — JARVIS Voice Agent [PORTED FROM FRIDAY + RENAMED]

```python
"""
Ayoub Voice Agent — JARVIS-style assistant over LiveKit.
Providers configurable via .env: STT, LLM, TTS.
Connects to ayoub-server (MCP) over SSE on port 8000.
"""

STT_PROVIDER = "sarvam"   # sarvam | whisper
LLM_PROVIDER = "gemini"   # gemini | openai (voice-compatible providers only)
TTS_PROVIDER = "openai"   # openai | sarvam

SYSTEM_PROMPT = """
You are Ayoub — a JARVIS-inspired AI assistant serving your user.

You are calm, precise, and attentive. You speak like a trusted aide...
[Full JARVIS-style personality prompt — see below for details]
"""
```

**JARVIS Personality** (replaces F.R.I.D.A.Y. prompt):
- Calls user **"sir"** (not "boss")
- After news brief → automatically calls `open_world_monitor`  
- Short 2-4 sentence spoken responses
- No markdown, no list items, no technical names
- Greeting: *"Good to see you, sir. What shall we tackle today?"*
- Tone: measured, intelligent, occasionally dry — JARVIS not FRIDAY

`AyoubVoiceAgent` class:
- Inherits `Agent` from `livekit.agents.voice`
- On init: builds `stt`, `llm`, `tts`, `vad`, MCP server connection (SSE `:8000`)
- `on_enter()` → greeting

Entry points: `main()` and `dev()` wrapper (same pattern as friday)

---

### `ayoub` — Main Bash CLI [RENAMED FROM `hereiz`]

The main CLI script (`ayoub`) is a complete rewrite of `hereiz` bash script with:
- All internal references to `hereiz` → `ayoub`
- Logging to `logs/ayoub.log` (was `hereiz.log`)
- Calls `./scripts/run_*.sh` with `ayoub` in log messages
- Full `usage()` output branded as `ayoub`

Complete flag map:

| Flag | Long form | Description |
|------|-----------|-------------|
| `-m 'question'` | `--main` | Full ReAct agent (default if no flag) |
| `-a 'question'` | `--ask` | Stateless Q&A (no memory) |
| `-aH 'question'` | | Ask + human-in-the-loop feedback |
| `-c 'question'` | `--chat` | Persistent memory chat |
| `-s 'query'` | `--search` | Web search + summarize |
| `-fs 'query'` | `--fullsearch` | Full search (scrapes many links) |
| `-G 'prompt'` | `--generate` | Generate images via Gradio |
| `-w 'question'` | `--screen` | Analyze current screen |
| `-t 'name'` | | Show a named template |
| `-tl` | | List all templates |
| `-memshow 'name'` | `--memory_show` | View a memory file |
| `-memclr 'name'` | `--memory_clear` | Clear a memory file |
| `-memlst` | `--memory_list` | List all memory files |
| `-searchshow` | `--search_show` | View search history |
| `-searchclr` | `--search_clear` | Clear search history |
| `-viewlogs` | | View log file |
| `-clrlogs` | | Clear log file |

Default (no flag): runs `-m` (main ReAct agent)

---

### `ayoub_screen.sh` [RENAMED FROM `hereiz_screen.sh`]

Screen capture helper script — renamed, all internal references updated from `hereiz` to `ayoub`.

---

### `scripts/` — Runner Scripts [ALL RENAMED]

Every script gets `ayoub` branding in log messages and Python import paths:

| Script | Calls |
|--------|-------|
| `run_main.sh` | `python3 -c "from ayoub.modules.main_agent import run_main; run_main('$1')"` |
| `run_ask.sh` | `from ayoub.modules.ask_agent import run_ask` |
| `run_askfeedback.sh` | `from ayoub.modules.ask_agent import run_ask; run_ask('$1', with_feedback=True)` |
| `run_chat.sh` | `from ayoub.modules.chat_agent import run_chat` |
| `run_search.sh` | `from ayoub.modules.search_agent import run_search` |
| `run_generate.sh` | `from ayoub.modules.generate_agent import run_generate` |
| `run_screen.sh` | `from ayoub.modules.screen_agent import run_screen` |
| `manage_logs.sh` | `cat logs/ayoub.log` / `> logs/ayoub.log` |
| `manage_memory.sh` | `from ayoub.memory.file_memory import ...` |
| `manage_search.sh` | reads/clears `data/search_history.txt` |
| `manage_templates.sh` | reads `templates/` directory |

---

### `.env.example` [NEW — COMPLETE]

```env
# ── LLM Provider ────────────────────────────────────────────────────────────
# Options: gemini | openai | groq | ollama
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.7

# ── Google Gemini ────────────────────────────────────────────────────────────
GOOGLE_API_KEY=your-google-api-key  # https://aistudio.google.com

# ── OpenAI ───────────────────────────────────────────────────────────────────
OPENAI_API_KEY=sk-proj-...          # https://platform.openai.com/api-keys

# ── Groq ─────────────────────────────────────────────────────────────────────
GROQ_API_KEY=gsk_...               # https://console.groq.com

# ── Ollama (local models — no API key needed) ─────────────────────────────────
OLLAMA_BASE_URL=http://localhost:11434
# Set LLM_PROVIDER=ollama and LLM_MODEL to any model you've pulled:
# ollama pull llama3   → LLM_MODEL=llama3
# ollama pull mistral  → LLM_MODEL=mistral
# ollama pull phi3     → LLM_MODEL=phi3
# ollama pull gemma3   → LLM_MODEL=gemma3
# ollama pull qwen2    → LLM_MODEL=qwen2

# ── Voice / LiveKit (optional — only needed for ayoub-voice) ─────────────────
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxx
STT_PROVIDER=sarvam                # sarvam | whisper
TTS_PROVIDER=openai                # openai | sarvam
SARVAM_API_KEY=sk_xxxxxxx          # https://dashboard.sarvam.ai

# ── MCP Server ────────────────────────────────────────────────────────────────
MCP_SERVER_PORT=8000
```

---

### `setup.sh` [NEW]

```bash
#!/bin/bash
set -e

echo "=== Ayoub AI Assistant — Setup ==="

# install uv if not present
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    pip install uv
fi

# install all Python deps
uv sync

# create required directories
mkdir -p data/memory data/tmp logs output/imgs output/sketches templates

# copy env template
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env created — fill in your API keys before running."
fi

# make CLI scripts executable
chmod +x ayoub ayoub_screen.sh scripts/*.sh

echo ""
echo "Setup complete! Usage:"
echo "  ayoub -a 'Your question'        (ask mode)"
echo "  ayoub -c 'Let's chat'           (chat with memory)"
echo "  ayoub -m 'Search for AI news'   (full ReAct agent)"
echo "  ayoub-server                    (start MCP tool server)"
echo "  ayoub-voice                     (start voice agent)"
echo ""
echo "To use Ollama: set LLM_PROVIDER=ollama and LLM_MODEL=llama3 in .env"
```

---

### `README.md` [NEW]

Will document:
- Project overview (JARVIS-style assistant)
- Architecture diagram
- Quick start (3 commands)
- All CLI flags table
- Provider switching table (Gemini/OpenAI/Groq/Ollama)
- Voice mode setup
- MCP server tools list

---

## Provider Switching Reference

| `LLM_PROVIDER` | `LLM_MODEL` examples | API Key needed |
|---|---|---|
| `gemini` | `gemini-2.5-flash`, `gemini-1.5-pro` | `GOOGLE_API_KEY` |
| `openai` | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` | `OPENAI_API_KEY` |
| `groq` | `llama-3.3-70b-versatile`, `mixtral-8x7b-32768` | `GROQ_API_KEY` |
| `ollama` | `llama3`, `mistral`, `phi3`, `gemma3`, `qwen2`, `deepseek-r1` | *(none — runs locally)* |

> [!TIP]
> To test Ollama quickly: `ollama pull llama3` then set `LLM_PROVIDER=ollama` + `LLM_MODEL=llama3` in `.env`

---

## Complete Rename Map (hereiz → ayoub)

| Old (hereiz) | New (ayoub) |
|---|---|
| `hereiz` (CLI command) | `ayoub` |
| `hereiz_screen.sh` | `ayoub_screen.sh` |
| `hereiz.log` | `ayoub.log` |
| `Hereiz` (in all prompts) | `Ayoub` |
| `"your name is Hereiz"` | `"your name is Ayoub"` |
| `from modules.X import ...` | `from ayoub.modules.X import ...` |
| `customAgents/` (external dep) | Built-in under `ayoub/agent/` |
| Class `FridayAgent` | Class `AyoubVoiceAgent` |
| Package `friday/` | Package `ayoub/mcp_server/` |
| Script `friday = "server:main"` | Script `ayoub-server = "ayoub.mcp_server.server:main"` |
| Script `friday_voice = "agent_friday:dev"` | Script `ayoub-voice = "ayoub.voice.agent:dev"` |
| `F.R.I.D.A.Y.` persona | `Ayoub / JARVIS` persona |
| `"boss"` (greeting term) | `"sir"` (JARVIS-style) |

---

## Verification Plan

### Step 1 — Install
```bash
cd c:\Users\ASUS\Downloads\Garv\Ayoub-AI-assistant
bash setup.sh
```
Expected: all deps install, directories created, `.env` copied.

### Step 2 — CLI Ask Mode
```bash
ayoub -a "What is the capital of France?"
```
Expected: streams answer from configured LLM provider.

### Step 3 — Ollama Mode
```bash
# in .env: LLM_PROVIDER=ollama, LLM_MODEL=llama3
ayoub -a "Explain quantum computing briefly"
```
Expected: response from local Ollama `llama3`.

### Step 4 — Chat with Memory
```bash
ayoub -c "My name is Ayoub and I love Python"
ayoub -c "What's my name?"    # should recall from memory
```

### Step 5 — ReAct Main Agent
```bash
ayoub -m "Search for the latest AI news and summarize the top 3 stories"
```
Expected: ReAct loop, search tool invoked, summary returned.

### Step 6 — MCP Server
```bash
ayoub-server   # starts on port 8000
```
Expected: FastMCP SSE server running.

### Step 7 — Voice (optional)
```bash
ayoub-voice    # requires LiveKit credentials in .env
```
Expected: connects to LiveKit, greets with JARVIS style.
