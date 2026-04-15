r"""
ayoub/cli.py — Interactive CLI for Ayoub-AI-assistant.

Registered as console_script 'ayoub' in pyproject.toml.
  Windows: .venv\Scripts\ayoub.exe
  Linux:   .venv/bin/ayoub

Running `ayoub` with no arguments launches the interactive menu.
All classic flags still work for one-shot usage.
"""

import sys
import os

# ── Colorama (cross-platform ANSI) ──────────────────────────────────────────
try:
    from colorama import init as _colorama_init, Fore, Style
    _colorama_init(autoreset=True)
except ImportError:
    # Graceful fallback — no colours
    class _NullFore:
        def __getattr__(self, _): return ""
    class _NullStyle:
        def __getattr__(self, _): return ""
    Fore = _NullFore()
    Style = _NullStyle()

from ayoub.logger import get_logger

logger = get_logger("cli")

# ── Palette ──────────────────────────────────────────────────────────────────
ORANGE  = Fore.YELLOW   # closest ANSI to orange; true orange needs 256-colour
BLUE    = Fore.CYAN     # bright cyan reads well as "question blue"
GREEN   = Fore.GREEN
RESET   = Style.RESET_ALL
BOLD    = Style.BRIGHT
DIM     = Style.DIM

# ── ASCII Banner ─────────────────────────────────────────────────────────────
BANNER = r"""
$$$$$$\  $$\     $$\  $$$$$$\  $$\   $$\ $$$$$$$\  
$$  __$$\ \$$\   $$  |$$  __$$\ $$ |  $$ |$$  __$$\ 
$$ /  $$ | \$$\ $$  / $$ /  $$ |$$ |  $$ |$$ |  $$ |
$$$$$$$$ |  \$$$$  /  $$ |  $$ |$$ |  $$ |$$$$$$$\ |
$$  __$$ |   \$$  /   $$ |  $$ |$$ |  $$ |$$  __$$\ 
$$ |  $$ |    $$ |    $$ |  $$ |$$ |  $$ |$$ |  $$ |
$$ |  $$ |    $$ |     $$$$$$  |\$$$$$$  |$$$$$$$  |
\__|  \__|    \__|     \______/  \______/ \_______/ 
"""

SUBTITLE = "  ✦  Your JARVIS-style AI assistant  —  v2.0.0  ✦"

# ── Goodbye Banner ───────────────────────────────────────────────────────────
GOODBYE_BANNER = r"""
░▒▓███████▓▒░▒▓████████▓▒░▒▓████████▓▒░      ░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░       ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░             ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░             ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
 ░▒▓██████▓▒░░▒▓██████▓▒░ ░▒▓██████▓▒░         ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
       ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
       ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░                ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░              
░▒▓███████▓▒░░▒▓████████▓▒░▒▓████████▓▒░         ░▒▓█▓▒░    ░▒▓██████▓▒░ ░▒▓██████▓▒░       ░▒▓█▓▒░ 
"""

# ── Interactive Menu Definition ───────────────────────────────────────────────
MENU = {
    "1":  ("Main Agent (ReAct)",      "main"),
    "2":  ("Stateless Q&A",           "ask"),
    "3":  ("Human Feedback Mode",     "ask_feedback"),
    "4":  ("Chat with Memory",        "chat"),
    "5":  ("Quick Web Search",        "search"),
    "6":  ("Full Scrape Search",      "fullsearch"),
    "7":  ("Generate Images",         "generate"),
    "8":  ("Analyze Screen",          "screen"),
    "9":  ("Show Prompt Template",    "template"),
    "10": ("List Templates",          "tl"),
    "11": ("Memory Management",       "memlst"),
    "12": ("Search History",          "searchshow"),
    "13": ("System Logs",             "viewlogs"),
    "14": ("Switch Model/Provider",   "switch"),
    "15": ("List Available Models",   "listmodels"),
    "16": ("Model Collaboration",     "collaborate"),
    "17": ("Exit",                    "exit"),
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _print_banner() -> None:
    """Print the orange ASCII banner."""
    print(ORANGE + BOLD + BANNER + RESET)
    print(ORANGE + SUBTITLE + RESET)
    print()


def _print_menu() -> None:
    """Print the numbered service menu."""
    print(BLUE + BOLD + "  ┌─────────────────────────────────────────┐" + RESET)
    print(BLUE + BOLD + "  │            SELECT A SERVICE              │" + RESET)
    print(BLUE + BOLD + "  └─────────────────────────────────────────┘" + RESET)
    print()
    for key, (label, _) in MENU.items():
        num  = (ORANGE + BOLD + f"  [{key:>2}]" + RESET)
        name = (GREEN + f"  {label}" + RESET) if label != "Exit" else (Fore.RED + f"  {label}" + RESET)
        print(f"{num}{name}")
    print()


def _ask_question(prompt: str) -> str:
    """Read user input with blue prompt styling."""
    try:
        return input(BLUE + BOLD + prompt + RESET).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def _system_prompt(text: str) -> None:
    """Print a dim system line."""
    print(DIM + text + RESET)


def _answer(text: str) -> None:
    """Print an answer / result line in green."""
    print(GREEN + text + RESET)


# ── Dispatcher — maps action keys to actual module calls ─────────────────────

def _dispatch(action: str, question: str = "") -> None:
    """Run the selected service."""

    if action == "main":
        if not question:
            question = _ask_question("  ▶  Ask Ayoub (ReAct): ")
        if question:
            from ayoub.modules.main_agent import run_main
            run_main(question)

    elif action == "ask":
        if not question:
            question = _ask_question("  ▶  Question: ")
        if question:
            from ayoub.modules.ask_agent import run_ask
            run_ask(question, with_feedback=False)

    elif action == "ask_feedback":
        if not question:
            question = _ask_question("  ▶  Question (with feedback): ")
        if question:
            from ayoub.modules.ask_agent import run_ask
            run_ask(question, with_feedback=True)

    elif action == "chat":
        if not question:
            question = _ask_question("  ▶  Chat message: ")
        if question:
            from ayoub.modules.chat_agent import run_chat
            run_chat(question)

    elif action == "search":
        if not question:
            question = _ask_question("  ▶  Search query: ")
        if question:
            from ayoub.modules.search_agent import run_search
            run_search(question, full=False)

    elif action == "fullsearch":
        if not question:
            question = _ask_question("  ▶  Full search query: ")
        if question:
            from ayoub.modules.search_agent import run_search
            run_search(question, full=True)

    elif action == "generate":
        if not question:
            question = _ask_question("  ▶  Image prompt: ")
        if question:
            from ayoub.modules.generate_agent import run_generate
            run_generate(question)

    elif action == "screen":
        if not question:
            question = _ask_question("  ▶  What do you want to know about your screen? ")
        if question:
            from ayoub.modules.screen_agent import run_screen
            run_screen(question)

    elif action == "template":
        name = question or _ask_question("  ▶  Template name: ")
        if name:
            from ayoub.config import TEMPLATES_DIR
            path = TEMPLATES_DIR / f"{name}.txt"
            _answer(path.read_text(encoding="utf-8") if path.exists()
                    else f"Template '{name}' not found in {TEMPLATES_DIR}")

    elif action == "tl":
        from ayoub.config import TEMPLATES_DIR
        files = sorted(TEMPLATES_DIR.glob("*.txt"))
        _answer("\n".join(f"  • {f.stem}" for f in files) if files else "  No templates found.")

    elif action == "memlst":
        from ayoub.modules.memory_agent import run_memlst
        run_memlst()

    elif action == "searchshow":
        from ayoub.config import SEARCH_HISTORY
        if SEARCH_HISTORY.exists():
            _answer(SEARCH_HISTORY.read_text(encoding="utf-8"))
        else:
            _answer("  No search history found.")

    elif action == "viewlogs":
        from ayoub.config import LOG_FILE
        if LOG_FILE.exists():
            _answer(LOG_FILE.read_text(encoding="utf-8"))
        else:
            _answer("  No log file found.")

    elif action == "switch":
        from ayoub.modules.model_switcher import run_switch
        run_switch()

    elif action == "listmodels":
        from ayoub.modules.model_switcher import run_list_models
        run_list_models()

    elif action == "collaborate":
        if not question:
            question = _ask_question("  ▶  Question for model collaboration: ")
        if question:
            from ayoub.modules.ollama_collab import run_collaborate
            run_collaborate(question)

    elif action == "exit":
        print(ORANGE + BOLD + GOODBYE_BANNER + RESET)
        sys.exit(0)

    else:
        print(Fore.RED + f"  Unknown action: {action}" + RESET)


# ── Interactive Session Loop ──────────────────────────────────────────────────

def _interactive_loop() -> None:
    """Show banner + menu, keep running until user chooses Exit."""
    _print_banner()

    while True:
        _print_menu()
        choice = _ask_question("  ▶  Enter service number: ")

        if not choice:          # Ctrl+C or empty — re-show menu
            print()
            continue

        if choice not in MENU:
            print(Fore.RED + f"\n  ✗  Invalid choice '{choice}'. Please pick 1–17.\n" + RESET)
            continue

        label, action = MENU[choice]
        print()
        _system_prompt(f"  ── {label} ──────────────────────────────────")
        print()

        try:
            _dispatch(action)
        except KeyboardInterrupt:
            print(ORANGE + BOLD + "\n  (interrupted — returning to menu)\n" + RESET)
            continue

        print()
        _ask_question("  Press Enter to return to menu...")
        print()


# ── Classic argparse (one-shot flags still work) ─────────────────────────────

_USAGE_EXAMPLES = """\
Examples:
  ayoub                                       (interactive menu — recommended)
  ayoub -a "What is quantum computing?"       (stateless Q&A)
  ayoub -aH "Explain recursion"               (ask + follow-up)
  ayoub -c "Let's continue our discussion"    (chat with memory)
  ayoub -m "Find the latest AI news"          (full ReAct agent)
  ayoub "What is 22 * 33?"                    (-m is the default)
  ayoub -s "best Python ML libraries"         (web search)
  ayoub -fs "deep learning papers 2024"       (full search)
  ayoub -G "a futuristic city at sunset"      (generate images)
  ayoub -w "What's on my screen?"             (screen analysis)
  ayoub -co "Explain black holes"             (4 Ollama models collaborate)
  ayoub -sw                                   (switch model interactively)
  ayoub -lm                                   (list all available models)
"""


def _build_parser():
    import argparse
    parser = argparse.ArgumentParser(
        prog="ayoub",
        description="Ayoub — JARVIS-style AI assistant (Windows + Linux)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_USAGE_EXAMPLES,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-m",  "--main",        metavar="Q", help="Full ReAct agent with all tools (default)")
    group.add_argument("-a",  "--ask",         metavar="Q", help="Stateless Q&A — no memory, no tools")
    group.add_argument("-aH",                  metavar="Q", dest="ask_feedback", help="Ask with human-in-the-loop follow-up")
    group.add_argument("-c",  "--chat",        metavar="Q", help="Chat with persistent memory")
    group.add_argument("-s",  "--search",      metavar="Q", help="Web search + summarise")
    group.add_argument("-fs", "--fullsearch",  metavar="Q", help="Full web search (scrapes multiple links)")
    group.add_argument("-G",  "--generate",    metavar="P", help="Generate images from a text prompt")
    group.add_argument("-w",  "--screen",      metavar="Q", help="Analyse current screen (screenshot + vision)")
    group.add_argument("-t",                   metavar="NAME", dest="template", help="Show a prompt template")
    group.add_argument("-tl",                  action="store_true", help="List all prompt templates")
    group.add_argument("-memshow",             metavar="NAME", help="Print contents of a memory file")
    group.add_argument("-memclr",              metavar="NAME", help="Delete a memory file")
    group.add_argument("-memlst",              action="store_true", help="List all memory files")
    group.add_argument("-searchshow",          action="store_true", help="Print search history")
    group.add_argument("-searchclr",           action="store_true", help="Clear search history")
    group.add_argument("-viewlogs",            action="store_true", help="Print the log file")
    group.add_argument("-clrlogs",             action="store_true", help="Clear the log file")
    group.add_argument("-sw", "--switch",      action="store_true", help="Interactive menu to switch provider / model")
    group.add_argument("-lm", "--listmodels",  action="store_true", help="List all available models by provider")
    group.add_argument("-co", "--collaborate", metavar="Q",         help="All 4 Ollama models collaborate on your question")

    # Bare positional — defaults to -m
    parser.add_argument("query", nargs="?", help="Question (defaults to main ReAct agent)")
    return parser


def main() -> None:
    # ── If no CLI flags given → drop into interactive menu ───────────────────
    if len(sys.argv) == 1:
        try:
            _interactive_loop()
        except KeyboardInterrupt:
            print(ORANGE + BOLD + GOODBYE_BANNER + RESET)
        return

    # ── Classic one-shot flag mode ────────────────────────────────────────────
    _print_banner()

    parser = _build_parser()
    args   = parser.parse_args()

    if args.ask:
        _dispatch("ask", args.ask)
    elif args.ask_feedback:
        _dispatch("ask_feedback", args.ask_feedback)
    elif args.chat:
        _dispatch("chat", args.chat)
    elif args.search:
        _dispatch("search", args.search)
    elif args.fullsearch:
        _dispatch("fullsearch", args.fullsearch)
    elif args.generate:
        _dispatch("generate", args.generate)
    elif args.screen:
        _dispatch("screen", args.screen)
    elif args.template:
        _dispatch("template", args.template)
    elif args.tl:
        _dispatch("tl")
    elif args.memshow:
        from ayoub.modules.memory_agent import run_memshow
        run_memshow(args.memshow)
    elif args.memclr:
        from ayoub.modules.memory_agent import run_memclr
        run_memclr(args.memclr)
    elif args.memlst:
        _dispatch("memlst")
    elif args.searchshow:
        _dispatch("searchshow")
    elif args.searchclr:
        from ayoub.config import SEARCH_HISTORY
        if SEARCH_HISTORY.exists():
            SEARCH_HISTORY.write_text("", encoding="utf-8")
            _answer("  Search history cleared.")
        else:
            _answer("  No search history found.")
    elif args.viewlogs:
        _dispatch("viewlogs")
    elif args.clrlogs:
        from ayoub.config import LOG_FILE
        if LOG_FILE.exists():
            LOG_FILE.write_text("", encoding="utf-8")
            _answer("  Log file cleared.")
    elif args.switch:
        _dispatch("switch")
    elif args.listmodels:
        _dispatch("listmodels")
    elif args.collaborate:
        _dispatch("collaborate", args.collaborate)
    elif args.main or args.query:
        _dispatch("main", args.main or args.query)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
