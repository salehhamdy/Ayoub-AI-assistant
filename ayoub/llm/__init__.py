"""
ayoub/llm/__init__.py — Provider factory.

Usage:
    from ayoub.llm import build_llm
    llm = build_llm()                              # uses .env settings
    llm = build_llm("ollama", "llama3")            # override at runtime
    llm = build_llm("groq", "llama-3.3-70b-versatile")
"""
from ayoub.config import (
    LLM_PROVIDER,
    LLM_MODEL,
    LLM_TEMPERATURE,
    GOOGLE_API_KEY,
    OPENAI_API_KEY,
    GROQ_API_KEY,
    OLLAMA_BASE_URL,
)


def build_llm(
    provider: str = LLM_PROVIDER,
    model: str = LLM_MODEL,
    temperature: float = LLM_TEMPERATURE,
):
    """
    Factory that returns the correct LLM adapter for the given provider.
    Provider defaults to LLM_PROVIDER from .env.
    """
    if provider == "gemini":
        from ayoub.llm.gemini import GeminiLLM
        return GeminiLLM(api_key=GOOGLE_API_KEY, model=model, temperature=temperature)

    elif provider == "openai":
        from ayoub.llm.openai_llm import OpenAILLM
        return OpenAILLM(api_key=OPENAI_API_KEY, model=model, temperature=temperature)

    elif provider == "groq":
        from ayoub.llm.groq_llm import GroqLLM
        return GroqLLM(api_key=GROQ_API_KEY, model=model, temperature=temperature)

    elif provider == "ollama":
        from ayoub.llm.ollama_llm import OllamaLLM
        return OllamaLLM(model=model, base_url=OLLAMA_BASE_URL, temperature=temperature)

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: {provider!r}\n"
            "Valid options: gemini | openai | groq | ollama"
        )
