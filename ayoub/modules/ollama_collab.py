"""
ayoub/modules/ollama_collab.py — Multi-model Ollama collaboration.

When you have multiple local Ollama models, this runs them ALL on your
query in parallel, prints each response, then has the best reasoner
(deepseek-r1:7b) synthesise a final unified answer.

Your 4 models and their roles:
  llama3.1       — General-purpose, balanced perspective
  mistral        — Concise, efficient analysis
  deepseek-r1:7b — Deep reasoning and logic (acts as final synthesiser)
  phi3           — Lightweight second opinion

Usage:
    ayoub -co "Your question here"
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from ayoub.config import OLLAMA_BASE_URL

# ── Model roster ──────────────────────────────────────────────────────────────
# These match the models you have installed.
# deepseek-r1:7b is used as the synthesis model at the end.
COLLAB_MODELS = [
    "llama3.1",
    "mistral",
    "deepseek-r1:7b",
    "phi3",
]

MODEL_ROLES = {
    "llama3.1":       "General Analyst",
    "mistral":        "Concise Analyst",
    "deepseek-r1:7b": "Deep Reasoner (Synthesiser)",
    "phi3":           "Second Opinion",
}

SYNTHESIS_MODEL = "deepseek-r1:7b"   # Best reasoner → final answer

_COLORS = {
    "llama3.1":       "\033[94m",  # blue
    "mistral":        "\033[92m",  # green
    "deepseek-r1:7b": "\033[95m",  # magenta
    "phi3":           "\033[93m",  # yellow
}
_RESET = "\033[0m"
_BOLD  = "\033[1m"


def _query_model(model: str, prompt: str) -> tuple[str, str]:
    """Query a single Ollama model. Returns (model, response)."""
    try:
        from ollama import Client
        client = Client(host=OLLAMA_BASE_URL)
        resp = client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return (model, resp.message.content.strip())
    except Exception as exc:
        return (model, f"[Error querying {model}: {exc}]")


def _available_collab_models() -> list[str]:
    """Return only the COLLAB_MODELS that are actually installed."""
    try:
        from ollama import Client
        client = Client(host=OLLAMA_BASE_URL)
        installed = {m.model.split(":")[0] for m in client.list().models}
        return [m for m in COLLAB_MODELS if m.split(":")[0] in installed or m in installed]
    except Exception:
        return COLLAB_MODELS  # assume all present if ollama is unreachable


def _print_header(text: str, color: str = "\033[96m") -> None:
    width = 66
    print(f"\n{_BOLD}{color}{'═' * width}{_RESET}")
    print(f"{_BOLD}{color}  {text}{_RESET}")
    print(f"{_BOLD}{color}{'═' * width}{_RESET}")


def run_collaborate(query: str) -> None:
    """
    1. Run every available Ollama model on `query` in parallel.
    2. Print each model's response.
    3. Send all responses to deepseek-r1:7b for synthesis.
    4. Print the final synthesised answer.
    """
    models = _available_collab_models()

    _print_header(f"🤝 Ayoub Collaboration — {len(models)} Models")
    print(f"\n  {_BOLD}Your question:{_RESET} {query}\n")

    # ── Phase 1: Parallel queries ─────────────────────────────────────────────
    print(f"  {_BOLD}⚡ Querying all models in parallel...{_RESET}\n")
    responses: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=len(models)) as pool:
        futures = {pool.submit(_query_model, m, query): m for m in models}
        for future in as_completed(futures):
            model, response = future.result()
            role  = MODEL_ROLES.get(model, model)
            color = _COLORS.get(model, "\033[97m")

            print(f"{_BOLD}{color}┌─ {model}  [{role}]{_RESET}")
            # wrap response lines
            for line in response.splitlines():
                print(f"{color}│  {line}{_RESET}")
            print(f"{color}└{'─' * 60}{_RESET}\n")

            responses[model] = response

    # ── Phase 2: Synthesis ────────────────────────────────────────────────────
    synthesiser = SYNTHESIS_MODEL if SYNTHESIS_MODEL in models else models[0]

    synthesis_prompt = (
        f"You are a synthesis AI. Multiple AI models answered the question below.\n"
        f"Your task: read all responses carefully, extract the best insights from each, "
        f"and produce ONE definitive, accurate, well-structured final answer.\n\n"
        f"Original question: {query}\n\n"
        + "\n\n".join(
            f"--- {m} [{MODEL_ROLES.get(m, m)}] ---\n{r}"
            for m, r in responses.items()
        )
        + "\n\n"
        f"Now write the best unified answer, drawing on all perspectives above:"
    )

    _print_header(f"🧠 Final Synthesis  [{synthesiser}]", color="\033[95m")
    print()

    try:
        from ollama import Client
        client = Client(host=OLLAMA_BASE_URL)
        stream = client.chat(
            model=synthesiser,
            messages=[{"role": "user", "content": synthesis_prompt}],
            stream=True,
        )
        for chunk in stream:
            print(chunk.message.content, end="", flush=True)
        print("\n")
    except Exception as exc:
        print(f"[Synthesis error: {exc}]")

    _print_header("✅ Collaboration Complete", color="\033[96m")
    print(f"  Models used: {', '.join(models)}\n")
