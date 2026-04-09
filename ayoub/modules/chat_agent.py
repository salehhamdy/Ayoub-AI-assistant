"""
ayoub/modules/chat_agent.py — Persistent memory chat agent.

CLI: ayoub -c "message"
Reads chat_memory on start, responds, then rewrites memory via AyoubMemoryAgent.
"""
from ayoub.agent.base_llm import AgentLLM
from ayoub.agent.base_prompt import BasePrompt
from ayoub.agent.base_runtime import BaseRuntime
from ayoub.agent.toolkit import ToolKit
from ayoub.memory.file_memory import read_memory
from ayoub.modules.memory_agent import AyoubMemoryAgent
from ayoub.logger import get_logger

logger = get_logger("chat-agent")

_SYSTEM_PROMPT = """\
You are Ayoub, a friendly and helpful AI assistant.
You remember the user's preferences and past interactions.
Your name is Ayoub.

Memory:
{memory}

Conversation:
Human: {question}
Ayoub:"""


def run_chat(question: str, memory_name: str = "chat_memory") -> str:
    """
    Respond to a question with memory context.
    After the response, update the memory file.
    """
    logger.info("ChatAgent invoked | question=%r", question[:80])

    memory_text = read_memory(memory_name)
    prompt_text = _SYSTEM_PROMPT.format(memory=memory_text or "(none yet)", question=question)

    prompt  = BasePrompt(prompt_string=prompt_text)
    llm     = AgentLLM()
    kit     = ToolKit()
    runtime = BaseRuntime(llm=llm, prompt=prompt, toolkit=kit)

    answer = runtime.step()

    # Update memory after responding
    conversation = f"Human: {question}\nAyoub: {answer}"
    AyoubMemoryAgent(memory_name).update(conversation)

    logger.info("ChatAgent completed.")
    return answer
