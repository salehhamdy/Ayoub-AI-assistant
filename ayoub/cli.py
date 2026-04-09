r"""
ayoub/cli.py — Cross-platform CLI for Ayoub-AI-assistant.

Registered as console_script 'ayoub' in pyproject.toml.
  Windows: .venv\Scripts\ayoub.exe
  Linux:   .venv/bin/ayoub

No bash required — pure Python argparse.
"""
import argparse
import sys

from ayoub.logger import get_logger

logger = get_logger("cli")

_USAGE_EXAMPLES = """\
Examples:
  ayoub -a "What is quantum computing?"          (stateless Q&A)
  ayoub -aH "Explain recursion"                  (ask + follow-up)
  ayoub -c "Let's continue our discussion"       (chat with memory)
  ayoub -m "Find the latest AI news"             (full ReAct agent)
  ayoub "What is 22 * 33?"                       (-m is the default)
  ayoub -s "best Python ML libraries"            (web search)
  ayoub -fs "deep learning papers 2024"          (full search)
  ayoub -G "a futuristic city at sunset"         (generate images)
  ayoub -w "What's on my screen?"                (screen analysis)
  ayoub -t my_template                           (show template)
  ayoub -tl                                      (list templates)
  ayoub -memshow chat_memory                     (view memory)
  ayoub -memclr chat_memory                      (clear memory)
  ayoub -memlst                                  (list memories)
  ayoub -searchshow                              (view search history)
  ayoub -searchclr                               (clear search history)
  ayoub -viewlogs                                (view log file)
  ayoub -clrlogs                                 (clear log file)
"""


def _build_parser() -> argparse.ArgumentParser:
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

    # Bare positional — defaults to -m
    parser.add_argument("query", nargs="?", help="Question (defaults to main ReAct agent)")
    return parser


def main() -> None:
    parser = _build_parser()
    args   = parser.parse_args()

    # ── Determine effective question ──────────────────────────────────────────
    question = (
        args.main or args.ask or args.ask_feedback or args.chat
        or args.search or args.fullsearch or args.generate or args.screen
        or args.query
    )

    # ── Dispatch ─────────────────────────────────────────────────────────────

    if args.ask:
        from ayoub.modules.ask_agent import run_ask
        run_ask(args.ask, with_feedback=False)

    elif args.ask_feedback:
        from ayoub.modules.ask_agent import run_ask
        run_ask(args.ask_feedback, with_feedback=True)

    elif args.chat:
        from ayoub.modules.chat_agent import run_chat
        run_chat(args.chat)

    elif args.search:
        from ayoub.modules.search_agent import run_search
        run_search(args.search, full=False)

    elif args.fullsearch:
        from ayoub.modules.search_agent import run_search
        run_search(args.fullsearch, full=True)

    elif args.generate:
        from ayoub.modules.generate_agent import run_generate
        run_generate(args.generate)

    elif args.screen:
        from ayoub.modules.screen_agent import run_screen
        run_screen(args.screen)

    elif args.template:
        from ayoub.config import TEMPLATES_DIR
        path = TEMPLATES_DIR / f"{args.template}.txt"
        print(path.read_text(encoding="utf-8") if path.exists()
              else f"Template '{args.template}' not found in {TEMPLATES_DIR}")

    elif args.tl:
        from ayoub.config import TEMPLATES_DIR
        files = sorted(TEMPLATES_DIR.glob("*.txt"))
        print("\n".join(f.stem for f in files) if files else "No templates found.")

    elif args.memshow:
        from ayoub.modules.memory_agent import run_memshow
        run_memshow(args.memshow)

    elif args.memclr:
        from ayoub.modules.memory_agent import run_memclr
        run_memclr(args.memclr)

    elif args.memlst:
        from ayoub.modules.memory_agent import run_memlst
        run_memlst()

    elif args.searchshow:
        from ayoub.config import SEARCH_HISTORY
        print(SEARCH_HISTORY.read_text(encoding="utf-8")
              if SEARCH_HISTORY.exists() else "No search history found.")

    elif args.searchclr:
        from ayoub.config import SEARCH_HISTORY
        if SEARCH_HISTORY.exists():
            SEARCH_HISTORY.write_text("", encoding="utf-8")
            print("Search history cleared.")
        else:
            print("No search history found.")

    elif args.viewlogs:
        from ayoub.config import LOG_FILE
        print(LOG_FILE.read_text(encoding="utf-8")
              if LOG_FILE.exists() else "No log file found.")

    elif args.clrlogs:
        from ayoub.config import LOG_FILE
        if LOG_FILE.exists():
            LOG_FILE.write_text("", encoding="utf-8")
            print("Log file cleared.")

    elif args.main or args.query:
        # Default: main ReAct agent
        from ayoub.modules.main_agent import run_main
        run_main(args.main or args.query)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
