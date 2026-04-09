"""
ayoub/llm/openai_llm.py — OpenAI adapter via LangChain.
"""
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from ayoub.llm.base import AbstractLLM


class OpenAILLM(AbstractLLM):
    def __init__(self, api_key: str, model: str, temperature: float):
        self._chain = (
            ChatOpenAI(api_key=api_key, model=model, temperature=temperature)
            | StrOutputParser()
        )

    def generate(self, prompt: str) -> str:
        return self._chain.invoke(prompt)

    def stream(self, prompt: str):
        yield from self._chain.stream(prompt)
