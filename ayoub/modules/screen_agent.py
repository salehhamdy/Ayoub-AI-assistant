"""
ayoub/modules/screen_agent.py — Enhanced screen analysis agent.

CLI: ayoub -w "What's on my screen?"

Enhancements:
  - Auto-detects analysis MODE from the question
  - Structured, detailed system prompt per mode
  - 5 modes: describe / code / summarise / error / translate
  - Shows screenshot path and timestamp
  - Streams coloured response to terminal
  - Saves to screen memory after each call
"""
import re
from datetime import datetime
from colorama import Fore, Style

from ayoub.agent.base_llm import AgentLLM
from ayoub.memory.file_memory import read_memory
from ayoub.modules.memory_agent import AyoubMemoryAgent
from ayoub.screen_capture import capture_screen
from ayoub.config import TMP_DIR
from ayoub.logger import get_logger

logger = get_logger("screen-agent")


# ── Mode detection ────────────────────────────────────────────────────────────

_MODES = {
    "code": [
        "code", "error", "bug", "fix", "function", "variable", "python",
        "javascript", "syntax", "debug", "compile", "script", "class", "import",
    ],
    "error": [
        "error", "exception", "traceback", "crash", "fail", "broken",
        "wrong", "issue", "problem", "not working", "stack trace",
    ],
    "summarise": [
        "summarise", "summarize", "summary", "tldr", "brief", "key points",
        "main points", "overview", "outline", "digest",
    ],
    "translate": [
        "translate", "translation", "arabic", "french", "spanish", "german",
        "english", "language", "convert text",
    ],
    "ocr": [
        "read", "text", "extract text", "what does it say", "copy",
        "transcribe", "written", "words on", "text on",
    ],
}

# ── Prompt templates per mode ─────────────────────────────────────────────────

_PROMPTS = {
    "describe": """\
You are Ayoub, an expert visual analyst. The user has shared a screenshot of their screen.

Previous screen context:
{memory}

Analyse the screenshot and answer the user's question:
"{question}"

In your response:
1. Describe what you see on the screen (apps, windows, content)
2. Answer the specific question directly
3. Note anything unusual or interesting
4. Suggest any actions if relevant

Be specific and thorough.""",

    "code": """\
You are Ayoub, a senior software engineer. The user has shared a screenshot showing code.

Previous context:
{memory}

The user asks: "{question}"

Analyse the code visible on screen:
1. Identify the programming language and file type
2. Explain what the code does
3. Identify any bugs, errors, or issues
4. Suggest improvements or fixes with corrected code snippets if needed
5. Explain the fix clearly

Be precise and provide actionable code suggestions.""",

    "error": """\
You are Ayoub, a debugging expert. The user has shared a screenshot with an error or problem.

Previous context:
{memory}

The user asks: "{question}"

Diagnose the error visible on screen:
1. Identify the exact error message
2. Explain what caused it (root cause)
3. Provide step-by-step fix instructions
4. Provide corrected code or commands if applicable
5. Explain how to prevent this in future

Be direct — give the fix, not just the explanation.""",

    "summarise": """\
You are Ayoub, an intelligent reading assistant. The user has shared a screenshot of content.

Previous context:
{memory}

The user asks: "{question}"

Analyse the content visible on screen:
1. Identify the type of content (article, document, website, email, etc.)
2. Provide a clear, structured summary
3. Highlight the 3-5 most important key points
4. Note the source or author if visible
5. Mention anything the user should pay attention to

Keep the summary concise but complete.""",

    "translate": """\
You are Ayoub, a translation expert. The user has shared a screenshot with text to translate.

Previous context:
{memory}

The user asks: "{question}"

1. Extract all visible text from the screenshot
2. Identify the source language
3. Provide a full, accurate translation
4. Note any cultural context or nuances in the translation

Present the translation clearly with the original text alongside.""",

    "ocr": """\
You are Ayoub, a text extraction expert. The user wants text extracted from the screenshot.

Previous context:
{memory}

The user asks: "{question}"

Extract ALL text visible on the screen:
1. Transcribe every piece of text you can see, in reading order
2. Preserve formatting (headers, lists, paragraphs) where possible
3. Note the type of content (UI labels, document text, code, etc.)
4. If some text is unclear, indicate it with [unclear]

Be exhaustive — extract everything.""",
}


def _detect_mode(question: str) -> str:
    """Detect the best analysis mode based on keywords in the question."""
    ql = question.lower()
    scores = {mode: 0 for mode in _MODES}
    for mode, keywords in _MODES.items():
        for kw in keywords:
            if kw in ql:
                scores[mode] += 1
    # error mode trumps code mode if both match
    best = max(scores, key=lambda m: scores[m])
    if scores[best] == 0:
        return "describe"
    # Handle overlap: 'error' beats 'code'
    if scores.get("error", 0) > 0:
        return "error"
    return best


def run_screen(question: str, memory_name: str = "screen_memory") -> str:
    """
    Capture screen, auto-detect analysis mode, analyse with vision LLM,
    stream output, update screen memory.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("ScreenAgent invoked | question=%r", question[:80])

    # ── 1. Detect mode ────────────────────────────────────────────────────────
    mode = _detect_mode(question)
    print(
        f"\n{Fore.LIGHTCYAN_EX}[screen] Mode: {mode.upper()}  |  "
        f"{ts}{Style.RESET_ALL}"
    )

    # ── 2. Capture screenshot ─────────────────────────────────────────────────
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        img_path = capture_screen(TMP_DIR)
        print(f"{Fore.LIGHTCYAN_EX}[screen] Screenshot: {img_path}{Style.RESET_ALL}")
    except Exception as exc:
        return f"[screen_agent] Could not capture screen: {exc}"

    # ── 3. Build prompt ───────────────────────────────────────────────────────
    memory_text  = read_memory(memory_name) or "(no previous screen interactions)"
    template     = _PROMPTS.get(mode, _PROMPTS["describe"])
    prompt_text  = template.format(memory=memory_text, question=question)

    # ── 4. Vision LLM call ────────────────────────────────────────────────────
    print(f"{Fore.LIGHTYELLOW_EX}[screen] Analysing screenshot...{Style.RESET_ALL}\n")
    llm    = AgentLLM()
    answer = llm.multimodal_generate(prompt=prompt_text, img_path=str(img_path))

    # Print with colour
    print(Fore.LIGHTGREEN_EX + answer + Style.RESET_ALL)

    # ── 5. Save to memory ─────────────────────────────────────────────────────
    conversation = (
        f"[{ts}] Mode: {mode}\n"
        f"Human: {question}\n"
        f"Ayoub: {answer[:500]}"
    )
    AyoubMemoryAgent(memory_name).update(conversation)

    logger.info("ScreenAgent completed | mode=%s", mode)
    return answer
