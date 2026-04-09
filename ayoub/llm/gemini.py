"""
ayoub/llm/gemini.py — Google Gemini adapter via LangChain.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from ayoub.llm.base import AbstractLLM


class GeminiLLM(AbstractLLM):
    def __init__(self, api_key: str, model: str, temperature: float):
        self._chain = (
            ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model=model,
                temperature=temperature,
            )
            | StrOutputParser()
        )

    def generate(self, prompt: str) -> str:
        return self._chain.invoke(prompt)

    def stream(self, prompt: str):
        yield from self._chain.stream(prompt)
