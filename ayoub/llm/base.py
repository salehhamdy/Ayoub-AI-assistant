"""
ayoub/llm/base.py — Abstract interface that every LLM adapter must implement.
"""
from abc import ABC, abstractmethod


class AbstractLLM(ABC):
    """Universal interface for all provider adapters (Gemini, OpenAI, Groq, Ollama)."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a complete response for the given prompt string."""
        ...

    @abstractmethod
    def stream(self, prompt: str):
        """Yield response tokens one at a time (generator)."""
        ...
