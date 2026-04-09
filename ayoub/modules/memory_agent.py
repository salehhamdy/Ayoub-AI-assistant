"""
ayoub/modules/memory_agent.py — Memory management agent and CLI helpers.

Used internally by chat_agent and screen_agent.
Also exposes run_memshow / run_memclr / run_memlst for CLI.
"""
from ayoub.agent.base_llm import AgentLLM
from ayoub.agent.base_prompt import BasePrompt
from ayoub.agent.base_runtime import BaseRuntime
from ayoub.agent.toolkit import ToolKit
from ayoub.memory.file_memory import (
    read_memory, write_memory, clear_memory, list_memories, show_memory
)
from ayoub.logger import get_logger

logger = get_logger("memory-agent")

_MEMORY_PROMPT = """\
You are Ayoub's internal memory manager.
Given the following conversation, extract and rewrite the memory in two sections:

## Long-term Memory
(Persistent facts about the user: name, preferences, goals, skills)

## Short-term Memory
(Key points from the most recent conversation)

Current memory:
{current_memory}

New conversation:
{conversation}

Rewrite the full memory now:"""


class AyoubMemoryAgent:
    """
    Summarises a conversation and rewrites the memory file.
    Called after every chat or screen interaction.
    """

    def __init__(self, memory_name: str = "chat_memory"):
        self._memory_name = memory_name
        self._llm = AgentLLM()

    def update(self, conversation: str) -> str:
        """Distil conversation into updated long-term + short-term memory."""
        current = read_memory(self._memory_name)
        prompt_text = _MEMORY_PROMPT.format(
            current_memory=current or "(empty)",
            conversation=conversation,
        )
        updated = self._llm.invoke_response(prompt_text)
        write_memory(self._memory_name, updated)
        logger.info("Memory '%s' updated.", self._memory_name)
        return updated


# ── Standalone CLI helpers ────────────────────────────────────────────────────

def run_memshow(name: str) -> None:
    show_memory(name)

def run_memclr(name: str) -> None:
    clear_memory(name)

def run_memlst() -> None:
    memories = list_memories()
    if memories:
        print("\nMemory files:")
        for m in memories:
            print(f"  - {m}")
    else:
        print("No memory files found.")
