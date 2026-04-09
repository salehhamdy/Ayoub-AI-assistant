"""
ayoub/memory/file_memory.py — Persistent file-based memory.

All paths use pathlib.Path for Windows + Linux compatibility.
Memory files are stored in data/memory/<name>.txt
"""
from pathlib import Path
from ayoub.config import MEMORY_DIR


def _ensure_dir() -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def read_memory(name: str) -> str:
    """Return the content of memory file <name>. Empty string if not found."""
    _ensure_dir()
    path: Path = MEMORY_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_memory(name: str, content: str) -> None:
    """Write (overwrite) memory file <name> with content."""
    _ensure_dir()
    (MEMORY_DIR / f"{name}.txt").write_text(content, encoding="utf-8")


def append_memory(name: str, content: str) -> None:
    """Append content to memory file <name>."""
    _ensure_dir()
    path: Path = MEMORY_DIR / f"{name}.txt"
    with path.open("a", encoding="utf-8") as f:
        f.write(content)


def clear_memory(name: str) -> None:
    """Delete memory file <name>."""
    path: Path = MEMORY_DIR / f"{name}.txt"
    if path.exists():
        path.unlink()
        print(f"[ayoub] Memory '{name}' cleared.")
    else:
        print(f"[ayoub] Memory '{name}' not found.")


def list_memories() -> list[str]:
    """Return names of all memory files (without .txt extension)."""
    _ensure_dir()
    return [p.stem for p in sorted(MEMORY_DIR.glob("*.txt"))]


def show_memory(name: str) -> str:
    """Print and return the content of memory file <name>."""
    content = read_memory(name)
    if content:
        print(f"\n{'='*40}\nMemory: {name}\n{'='*40}\n{content}\n{'='*40}")
    else:
        print(f"[ayoub] Memory '{name}' is empty or does not exist.")
    return content
