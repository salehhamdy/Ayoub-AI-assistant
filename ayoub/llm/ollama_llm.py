"""
ayoub/llm/ollama_llm.py — Ollama adapter for locally-running models.

Prerequisites:
  Install Ollama:
    Windows: https://ollama.com/download/windows
    Linux:   curl -fsSL https://ollama.com/install.sh | sh
  Pull a model:
    ollama pull llama3
  Set in .env:
    LLM_PROVIDER=ollama
    LLM_MODEL=llama3   (or: mistral, phi3, gemma3, qwen2, deepseek-r1, ...)
"""
import ollama as _ollama
from ayoub.llm.base import AbstractLLM


class OllamaLLM(AbstractLLM):
    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
    ):
        self.model = model
        self.temperature = temperature
        self._client = _ollama.Client(host=base_url)

    def generate(self, prompt: str) -> str:
        response = self._client.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temperature},
        )
        return response["response"]

    def stream(self, prompt: str):
        for chunk in self._client.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temperature},
            stream=True,
        ):
            yield chunk.get("response", "")
