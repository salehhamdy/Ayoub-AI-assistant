"""
ayoub/agent/base_llm.py — AgentLLM wrapper.

Wraps build_llm() and adds colorised streaming, invoke (non-streaming),
and multimodal generation for screen/vision tasks.
"""
import time
from typing import Optional
from colorama import Fore, Style

from ayoub.llm import build_llm
from ayoub.config import LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE, GOOGLE_API_KEY, API_CALL_DELAY

_STYLES = {
    "default":  "",
    "green":    Fore.LIGHTGREEN_EX,
    "blue":     Fore.LIGHTBLUE_EX,
    "yellow":   Fore.LIGHTYELLOW_EX,
    "cyan":     Fore.LIGHTCYAN_EX,
    "red":      Fore.LIGHTRED_EX,
    "magenta":  Fore.LIGHTMAGENTA_EX,
    "visual":   Fore.LIGHTMAGENTA_EX,
}


class AgentLLM:
    """
    High-level LLM wrapper used by all agent modules.
    Delegates to build_llm() for the actual provider.
    """

    def __init__(
        self,
        provider: str = LLM_PROVIDER,
        model: str = LLM_MODEL,
        temperature: float = LLM_TEMPERATURE,
    ):
        self._llm = build_llm(provider=provider, model=model, temperature=temperature)
        self._provider = provider
        self._model = model

    # ── Streaming (used by runtimes) ──────────────────────────────────────────

    def stream(self, prompt: str):
        """Yield raw text chunks from the LLM. Waits API_CALL_DELAY seconds first."""
        if API_CALL_DELAY > 0:
            time.sleep(API_CALL_DELAY)
        yield from self._llm.stream(prompt)

    def generate_response(self, prompt: str, output_style: str = "cyan") -> str:
        """Stream the response to stdout with colorama, return the full string."""
        color = _STYLES.get(output_style, "")
        response = ""
        for chunk in self._llm.stream(prompt):
            text = color + chunk + Style.RESET_ALL if color else chunk
            print(text, end="", flush=True)
            response += chunk
        print()
        return response

    # ── Non-streaming (used for memory summarisation) ─────────────────────────

    def invoke_response(self, prompt: str) -> str:
        """Non-streaming single call — returns the complete response string."""
        if API_CALL_DELAY > 0:
            time.sleep(API_CALL_DELAY)
        return self._llm.generate(prompt)

    # ── ReAct compatibility alias ─────────────────────────────────────────────

    def llm_generate(self, input: str, output_style: str = "cyan") -> str:
        return self.generate_response(input, output_style)

    # ── Multimodal (vision) ───────────────────────────────────────────────────

    def multimodal_generate(self, prompt: str, img_path: Optional[str] = None) -> str:
        """
        Vision call using Google Gemini (google-genai 1.x SDK).
        Falls back to text-only if no image is provided.
        """
        if img_path is None:
            return self.invoke_response(prompt)

        try:
            from google import genai as google_genai
            from google.genai import types as genai_types
            from PIL import Image

            client = google_genai.Client(api_key=GOOGLE_API_KEY)
            img = Image.open(img_path)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, img],
            )
            return response.text
        except Exception as exc:
            return f"[Vision error: {exc}]"

    def __repr__(self) -> str:
        return f"AgentLLM(provider={self._provider!r}, model={self._model!r})"
