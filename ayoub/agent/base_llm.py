"""
ayoub/agent/base_llm.py — AgentLLM wrapper.

Wraps build_llm() and adds colorised streaming, invoke (non-streaming),
and multimodal generation for screen/vision tasks.
"""
import time
from typing import Optional
from colorama import Fore, Style

from ayoub.llm import build_llm
from ayoub.config import LLM_PROVIDER, LLM_MODEL, LLM_TEMPERATURE, GOOGLE_API_KEY, GROQ_API_KEY, API_CALL_DELAY

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
        Vision analysis cascade:
          1. Google Gemini  gemini-2.0-flash       (best quality)
          2. Groq Vision    llama-3.2-90b-vision   (free fallback, no quota issues)
        Falls back to text-only if no image is provided.
        """
        if img_path is None:
            return self.invoke_response(prompt)

        # ── 1. Try Gemini Vision ──────────────────────────────────────────────
        if GOOGLE_API_KEY:
            try:
                from google import genai as google_genai
                from PIL import Image

                client  = google_genai.Client(api_key=GOOGLE_API_KEY)
                img     = Image.open(img_path)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[prompt, img],
                )
                return response.text
            except Exception as gemini_exc:
                _is_quota = "429" in str(gemini_exc) or "RESOURCE_EXHAUSTED" in str(gemini_exc)
                if _is_quota:
                    print("[vision] Gemini quota exhausted — switching to Groq Vision ...")
                else:
                    print(f"[vision] Gemini error: {gemini_exc}")

        # ── 2. Fallback: Groq Vision (base64) ────────────────────────────────
        if GROQ_API_KEY:
            # Current Groq vision models (in order of preference)
            _GROQ_VISION_MODELS = [
                "meta-llama/llama-4-scout-17b-16e-instruct",   # Llama 4 Scout (multimodal)
                "meta-llama/llama-4-maverick-17b-128e-instruct",# Llama 4 Maverick
                "llama-3.2-11b-vision-preview",                 # Older, might still work
            ]
            try:
                import base64
                from groq import Groq

                with open(img_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode("utf-8")

                ext  = str(img_path).rsplit(".", 1)[-1].lower()
                mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                        "png": "image/png",  "webp": "image/webp"}.get(ext, "image/png")

                groq_client = Groq(api_key=GROQ_API_KEY)

                for vision_model in _GROQ_VISION_MODELS:
                    try:
                        print(f"[vision] Trying Groq model: {vision_model}")
                        completion = groq_client.chat.completions.create(
                            model=vision_model,
                            messages=[{
                                "role": "user",
                                "content": [
                                    {"type": "text",      "text": prompt},
                                    {"type": "image_url", "image_url": {
                                        "url": f"data:{mime};base64,{img_b64}"
                                    }},
                                ],
                            }],
                            max_tokens=2048,
                        )
                        print(f"[vision] Using Groq model: {vision_model}")
                        return completion.choices[0].message.content
                    except Exception as model_exc:
                        print(f"[vision] {vision_model} failed: {model_exc}")
                        continue

            except Exception as groq_exc:
                print(f"[vision] Groq Vision error: {groq_exc}")

        return "[Vision error: No vision provider available. Check GOOGLE_API_KEY or GROQ_API_KEY.]"

    def __repr__(self) -> str:
        return f"AgentLLM(provider={self._provider!r}, model={self._model!r})"
