"""
ayoub/modules/model_switcher.py — Interactive provider/model switcher.

Writes the chosen provider and model directly to .env.
Fetches installed Ollama models dynamically via `ollama list`.

Usage:
    ayoub -sw     # Interactive numbered menu
    ayoub -lm     # Print-only list of all models
"""
import os
import re
import subprocess
import sys
from pathlib import Path

# ── Static model catalog ──────────────────────────────────────────────────────
CATALOG: dict[str, list[str]] = {
    "gemini": [
        "gemini-1.5-flash",      # fast, free tier ✅
        "gemini-1.5-pro",        # more capable
        "gemini-2.0-flash",      # newest stable
        "gemini-2.0-flash-exp",  # experimental
    ],
    "groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "llama3-70b-8192",
        "llama3-8b-8192",
    ],
    "deepseek": [
        "deepseek-chat",
        "deepseek-reasoner",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-3.5-turbo",
    ],
    "ollama": [],  # populated dynamically from `ollama list`
}

_PROVIDER_DESCRIPTIONS = {
    "gemini":   "Google Gemini      — free tier, vision support",
    "groq":     "Groq               — ultra-fast inference, free",
    "deepseek": "DeepSeek           — best reasoning, very cheap",
    "openai":   "OpenAI             — GPT-4o, requires paid key",
    "ollama":   "Ollama (local)     — offline, private, no API key",
}


def _get_ollama_models() -> list[str]:
    """Return list of locally installed Ollama model names."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().splitlines()
        models = []
        for line in lines[1:]:  # skip header row
            parts = line.split()
            if parts:
                name = parts[0].rstrip(":latest").strip()
                if name:
                    models.append(name)
        return models
    except Exception:
        return []


def _current_settings() -> tuple[str, str]:
    """Read current LLM_PROVIDER and LLM_MODEL from .env."""
    from ayoub.config import LLM_PROVIDER, LLM_MODEL
    return LLM_PROVIDER, LLM_MODEL


def _write_to_env(provider: str, model: str) -> bool:
    """
    Update LLM_PROVIDER and LLM_MODEL lines in .env.
    Returns True on success.
    """
    # Find .env — walk up from here or use project root
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if not env_path.exists():
        print(f"[model_switcher] .env not found at {env_path}")
        return False

    content = env_path.read_text(encoding="utf-8")

    # Replace or append LLM_PROVIDER
    if re.search(r"^LLM_PROVIDER\s*=", content, re.MULTILINE):
        content = re.sub(
            r"^LLM_PROVIDER\s*=.*$",
            f"LLM_PROVIDER={provider}",
            content, flags=re.MULTILINE
        )
    else:
        content = f"LLM_PROVIDER={provider}\n" + content

    # Replace or append LLM_MODEL
    if re.search(r"^LLM_MODEL\s*=", content, re.MULTILINE):
        content = re.sub(
            r"^LLM_MODEL\s*=.*$",
            f"LLM_MODEL={model}",
            content, flags=re.MULTILINE
        )
    else:
        content = f"LLM_MODEL={model}\n" + content

    env_path.write_text(content, encoding="utf-8")
    return True


def run_list_models() -> None:
    """Print all available models grouped by provider."""
    current_provider, current_model = _current_settings()
    ollama_installed = _get_ollama_models()

    catalog = dict(CATALOG)
    catalog["ollama"] = ollama_installed or ["(no models installed — run: ollama pull llama3.1)"]

    print("\n" + "═" * 58)
    print("  Ayoub — Available AI Models")
    print("═" * 58)
    print(f"  Current: [{current_provider}] {current_model}\n")

    for provider, models in catalog.items():
        marker = "▶" if provider == current_provider else " "
        desc = _PROVIDER_DESCRIPTIONS.get(provider, provider)
        print(f"  {marker} {desc}")
        for m in models:
            active = "✓" if (provider == current_provider and m == current_model) else " "
            print(f"      [{active}] {m}")
        print()

    print("  Switch with:  ayoub -sw")
    print("═" * 58 + "\n")


def run_switch() -> None:
    """Interactive numbered menu to switch provider and model."""
    current_provider, current_model = _current_settings()
    ollama_installed = _get_ollama_models()

    catalog = dict(CATALOG)
    catalog["ollama"] = ollama_installed if ollama_installed else []

    # Build flat list: (display_string, provider, model)
    options: list[tuple[str, str, str]] = []
    for provider, models in catalog.items():
        desc = _PROVIDER_DESCRIPTIONS.get(provider, provider)
        for model in models:
            active = " ✓" if (provider == current_provider and model == current_model) else ""
            label = f"{desc}  →  {model}{active}"
            options.append((label, provider, model))

    if not options:
        print("[model_switcher] No models found.")
        return

    # Print menu
    print("\n" + "═" * 64)
    print("  Ayoub — Switch Model")
    print(f"  Current: [{current_provider}] {current_model}")
    print("═" * 64)
    for i, (label, _, _) in enumerate(options, 1):
        print(f"  {i:>3}.  {label}")
    print("═" * 64)
    print("  Enter number to switch  (or 0 / Enter to cancel)\n")

    try:
        raw = input("  Your choice: ").strip()
        if not raw or raw == "0":
            print("  No change.")
            return
        choice = int(raw)
        if not (1 <= choice <= len(options)):
            print("  Invalid number.")
            return
    except (ValueError, KeyboardInterrupt):
        print("\n  Cancelled.")
        return

    _, new_provider, new_model = options[choice - 1]

    if new_provider == current_provider and new_model == current_model:
        print(f"\n  Already using [{new_provider}] {new_model}. No change.")
        return

    if _write_to_env(new_provider, new_model):
        print(f"\n  ✅ Switched to [{new_provider}] {new_model}")
        print("  Change saved to .env — effective immediately.\n")
    else:
        print("  ❌ Failed to update .env")
