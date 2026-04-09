"""
ayoub/llm/deepseek_llm.py — DeepSeek adapter (OpenAI-compatible API).

DeepSeek's API is 100% OpenAI-compatible, so we use ChatOpenAI
with a custom base_url pointing to https://api.deepseek.com

Models:
  deepseek-chat       — fast, general purpose  (~GPT-4o level)
  deepseek-reasoner   — deep reasoning (R1)    (~o1 level)

Usage in .env:
  LLM_PROVIDER=deepseek
  LLM_MODEL=deepseek-chat
  DEEPSEEK_API_KEY=sk-...
"""
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from ayoub.llm.base import AbstractLLM


class DeepSeekLLM(AbstractLLM):
    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        base_url: str = "https://api.deepseek.com",
    ):
        self._chain = (
            ChatOpenAI(
                api_key=api_key,
                model=model,
                temperature=temperature,
                base_url=base_url,
            )
            | StrOutputParser()
        )

    def generate(self, prompt: str) -> str:
        return self._chain.invoke(prompt)

    def stream(self, prompt: str):
        yield from self._chain.stream(prompt)
