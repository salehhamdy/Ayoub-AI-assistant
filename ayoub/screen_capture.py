"""
ayoub/screen_capture.py — Cross-platform screen capture.

Windows → PIL.ImageGrab.grab()
Linux   → scrot (if available) or PIL.ImageGrab (requires display)
"""
import platform
import shutil
import subprocess
from pathlib import Path


def capture_screen(output_dir: Path) -> Path:
    """
    Take a screenshot and save it to output_dir/screenshot.png.
    Returns the Path to the saved file.
    Works on Windows and Linux.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    out: Path = output_dir / "screenshot.png"
    system = platform.system()

    if system == "Windows":
        _capture_windows(out)
    elif system == "Linux":
        _capture_linux(out)
    else:
        raise OSError(f"Screen capture is not supported on {system}.")

    return out


def _capture_windows(out: Path) -> None:
    """Use PIL.ImageGrab — works natively on Windows with Pillow."""
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        img.save(str(out))
    except ImportError:
        raise ImportError(
            "Pillow is required for screen capture on Windows.\n"
            "Run: pip install pillow"
        )


def _capture_linux(out: Path) -> None:
    """
    Try scrot first (fastest, works with X11).
    Fall back to PIL.ImageGrab if scrot is not installed.
    """
    if shutil.which("scrot"):
        subprocess.run(["scrot", str(out)], check=True)
    else:
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            img.save(str(out))
        except Exception as exc:
            raise RuntimeError(
                f"Screen capture failed on Linux. "
                f"Install scrot (`sudo apt install scrot`) or Pillow.\n{exc}"
            )
