"""
helpers/sketch_window.py — Cross-platform tkinter sketch canvas.

Windows: tkinter is bundled with Python.
Linux:   install python3-tk  (sudo apt install python3-tk)
"""
import tempfile
from pathlib import Path

try:
    import tkinter as tk
    from PIL import Image, ImageDraw
    _TK_AVAILABLE = True
except ImportError:
    _TK_AVAILABLE = False


def sketch_window() -> str:
    """
    Open a blank white canvas (512×512).
    The user draws with the left mouse button.
    Close the window to confirm.
    Returns the path to the saved PNG file.
    """
    if not _TK_AVAILABLE:
        raise ImportError(
            "tkinter or Pillow is not available.\n"
            "Linux: sudo apt install python3-tk\n"
            "Then: pip install pillow"
        )

    root = tk.Tk()
    root.title("Ayoub Sketch — draw, then close the window")

    canvas = tk.Canvas(root, width=512, height=512, bg="white", cursor="crosshair")
    canvas.pack()

    image = Image.new("RGB", (512, 512), "white")
    draw  = ImageDraw.Draw(image)

    _last: dict = {}

    def on_press(event):
        _last["x"] = event.x
        _last["y"] = event.y

    def on_drag(event):
        x0, y0 = _last.get("x", event.x), _last.get("y", event.y)
        x1, y1 = event.x, event.y
        r = 4
        canvas.create_oval(x1 - r, y1 - r, x1 + r, y1 + r, fill="black", outline="")
        draw.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill="black")
        _last["x"] = x1
        _last["y"] = y1

    canvas.bind("<ButtonPress-1>",  on_press)
    canvas.bind("<B1-Motion>",      on_drag)

    root.mainloop()

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    image.save(tmp.name)
    return tmp.name
