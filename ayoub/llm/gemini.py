"""
ayoub/llm/gemini.py — Google Gemini adapter using the google-genai SDK (1.x).

Uses `from google import genai` (new unified SDK) — avoids the broken
`google-generativeai` gRPC v1beta endpoint that dropped gemini-1.5 models.

Valid model names for this SDK:
  gemini-2.0-flash          ← default, fast, free tier  ✅
  gemini-2.0-flash-lite     ← smallest/cheapest
  gemini-1.5-pro            ← long context (may need v1)
  gemini-2.5-pro-preview-03-25  ← preview

To switch model:  ayoub -sw   OR edit LLM_MODEL in .env
"""
from google import genai
from google.genai import types

from ayoub.llm.base import AbstractLLM


class GeminiLLM(AbstractLLM):
    def __init__(self, api_key: str, model: str, temperature: float):
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._config = types.GenerateContentConfig(temperature=temperature)

    def generate(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=self._config,
        )
        return response.text

    def stream(self, prompt: str):
        """Stream response chunks token by token."""
        for chunk in self._client.models.generate_content_stream(
            model=self._model,
            contents=prompt,
            config=self._config,
        ):
            try:
                if chunk.text:
                    yield chunk.text
            except Exception:
                continue
