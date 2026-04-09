"""
ayoub/modules/screen_agent.py — Screen analysis agent (multimodal / vision).

CLI: ayoub -w "What's on my screen?"

Takes a screenshot, passes it to the vision LLM, then updates screen memory.
"""
from ayoub.agent.base_llm import AgentLLM
from ayoub.agent.base_prompt import BasePrompt
from ayoub.agent.base_runtime import BaseRuntime
from ayoub.agent.toolkit import ToolKit
from ayoub.memory.file_memory import read_memory
from ayoub.modules.memory_agent import AyoubMemoryAgent
from ayoub.screen_capture import capture_screen
from ayoub.config import TMP_DIR
from ayoub.logger import get_logger

logger = get_logger("screen-agent")

_SYSTEM_PROMPT = """\
You are Ayoub. You can see the user's screen via the attached screenshot.

Screen memory (previous interactions):
{memory}

The user asks: {question}

Respond helpfully based on what you see in the screenshot."""


def run_screen(question: str, memory_name: str = "screen_memory") -> str:
    """Capture screen, analyse with vision LLM, update screen memory."""
    logger.info("ScreenAgent invoked | question=%r", question[:80])

    # 1. Capture screenshot
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        img_path = capture_screen(TMP_DIR)
    except Exception as exc:
        return f"[screen_agent] Could not capture screen: {exc}"

    # 2. Build prompt with memory
    memory_text = read_memory(memory_name)
    prompt_text = _SYSTEM_PROMPT.format(
        memory=memory_text or "(none yet)",
        question=question,
    )

    # 3. Multimodal call
    llm    = AgentLLM()
    answer = llm.multimodal_generate(prompt=prompt_text, img_path=str(img_path))
    print(answer)

    # 4. Update screen memory
    conversation = f"Human: {question}\nAyoub: {answer}"
    AyoubMemoryAgent(memory_name).update(conversation)

    logger.info("ScreenAgent completed.")
    return answer
