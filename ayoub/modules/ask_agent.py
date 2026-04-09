"""
ayoub/modules/ask_agent.py — Stateless Q&A agent.

CLI: ayoub -a "question"
     ayoub -aH "question"   (with human-in-the-loop)
"""
from ayoub.agent.base_llm import AgentLLM
from ayoub.agent.base_prompt import BasePrompt
from ayoub.agent.humanloop_runtime import HumanLoopRuntime
from ayoub.agent.toolkit import ToolKit
from ayoub.logger import get_logger

logger = get_logger("ask-agent")

_SYSTEM_PROMPT = """\
You are Ayoub, a helpful and friendly AI assistant.
You have deep expertise in programming, data science, machine learning, science, and mathematics.
Your name is Ayoub. When asked, always introduce yourself as Ayoub.
If you don't know something, say so honestly rather than guessing.
Be concise, accurate, and friendly.

Question: {question}
Ayoub:"""


def run_ask(question: str, with_feedback: bool = False) -> str:
    """
    Run a stateless, single-turn Q&A.
    with_feedback=True activates the human-in-the-loop follow-up loop.
    """
    logger.info("AskAgent invoked | feedback=%s | question=%r", with_feedback, question[:80])

    prompt_text = _SYSTEM_PROMPT.format(question=question)
    prompt = BasePrompt(prompt_string=prompt_text)
    llm    = AgentLLM()
    kit    = ToolKit()   # no tools — stateless

    runtime = HumanLoopRuntime(llm=llm, prompt=prompt, toolkit=kit)
    answer  = runtime.loop(activate_loop=with_feedback)

    logger.info("AskAgent completed.")
    return answer
