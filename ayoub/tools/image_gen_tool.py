"""
ayoub/tools/image_gen_tool.py — Image generation tools via Gradio.

Ported from hereiz generate_agents.py:
  - AyoubTxt2ImgTool  → text-to-image   (mukaist/DALLE-4k)
  - AyoubSketch2ImgTool → sketch-to-image (gparmar-img2img-turbo-sketch)

Requires: gradio_client, matplotlib, pillow, tkinter (built-in on Windows;
          python3-tk on Linux).
"""
from ayoub.agent.toolkit import BaseTool
from ayoub.config import OUTPUT_IMGS_DIR, OUTPUT_SKETCHES


class AyoubTxt2ImgTool(BaseTool):
    """Generate images from a text prompt via DALL-E 4K Gradio space."""

    def __init__(
        self,
        description: str = "Generate images from a text prompt and save them locally",
        tool_name: str = "image_to_text_tool",
    ):
        super().__init__(description, tool_name)
        OUTPUT_IMGS_DIR.mkdir(parents=True, exist_ok=True)

    # Ordered list of Gradio spaces to try (first working one is used)
    _SPACES = [
        ("mukaist/DALLE-4k",           "/run"),
        ("stabilityai/sdxl-turbo",     "/predict"),
        ("hysts/SD-XL",                "/run"),
    ]

    def execute_func(self, prompt: str) -> str:
        try:
            from gradio_client import Client
            from helpers.image_utils import save_imgs, show_images_side_by_side
        except ImportError as exc:
            return f"[image_to_text_tool] Missing dependency: {exc}"

        prompt = prompt.strip()
        last_err = ""

        for space, api_name in self._SPACES:
            try:
                client = Client(space)
                result = client.predict(prompt, api_name=api_name)
                # result shape varies by space — normalise
                if isinstance(result, list) and result and isinstance(result[0], list):
                    img_dirs = [r["image"] for r in result[0] if isinstance(r, dict)]
                elif isinstance(result, list):
                    img_dirs = [r for r in result if isinstance(r, str)]
                else:
                    img_dirs = [str(result)]

                if not img_dirs:
                    continue

                saved = save_imgs(img_dirs, str(OUTPUT_IMGS_DIR))
                show_images_side_by_side(str(OUTPUT_IMGS_DIR))
                return f"Images saved to: {', '.join(saved)}"
            except Exception as exc:
                last_err = f"[{space}] {exc}"
                continue

        return f"[image_to_text_tool] All spaces unavailable. Last error: {last_err}"


class AyoubSketch2ImgTool(BaseTool):
    """Open a sketch window, then refine the drawing into an image via Gradio."""

    def __init__(
        self,
        description: str = "Open a drawing canvas, sketch something, then generate an image from it",
        tool_name: str = "sketch_to_image_tool",
    ):
        super().__init__(description, tool_name)
        OUTPUT_SKETCHES.mkdir(parents=True, exist_ok=True)

    def execute_func(self, prompt: str) -> str:
        try:
            from gradio_client import Client
            from helpers.sketch_window import sketch_window
            from helpers.image_utils import save_imgs, show_images_side_by_side

            img_path = sketch_window()   # cross-platform tkinter canvas

            client = Client("https://gparmar-img2img-turbo-sketch.hf.space/")
            result = client.predict(
                img_path,
                prompt.strip(),
                "ethereal fantasy concept art of {prompt}",
                "Fantasy art",
                "42",
                0.4,
                fn_index=9,
            )
            saved = save_imgs([result[0]], str(OUTPUT_SKETCHES))
            show_images_side_by_side(str(OUTPUT_SKETCHES))
            return f"Sketch image saved to: {', '.join(saved)}"
        except Exception as exc:
            return f"[sketch_to_image_tool] Error: {exc}"
