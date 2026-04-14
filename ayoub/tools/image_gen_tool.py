"""
ayoub/tools/image_gen_tool.py — Enhanced image generation.

PRIMARY: Pollinations.ai  — free, no API key, reliable, 6 models
FALLBACK: Gradio spaces   — tried if Pollinations fails

Pollinations models:
  flux           — default, high quality
  flux-realism   — photorealistic photography
  flux-anime     — anime / manga style
  flux-3d        — 3D render style
  flux-cablyai   — artistic / painting
  turbo          — fast generation

Usage:
  ayoub -G "a futuristic city at sunset"
  ayoub -G "photorealistic portrait of a wise wizard"
  ayoub -G "anime girl in a cherry blossom forest"
"""
import os
import re
import time
from datetime import datetime
from pathlib import Path

import requests

from ayoub.agent.toolkit import BaseTool
from ayoub.config import OUTPUT_IMGS_DIR, OUTPUT_SKETCHES

# ── Pollinations config ───────────────────────────────────────────────────────
_POLLINATIONS_BASE = "https://image.pollinations.ai/prompt/{prompt}"
_DEFAULT_WIDTH  = 1024
_DEFAULT_HEIGHT = 1024
_TIMEOUT        = 60  # seconds to wait for generation

# ── Style auto-detection ──────────────────────────────────────────────────────
_STYLE_KEYWORDS = {
    "flux-realism":  ["photo", "photorealistic", "realistic", "portrait", "4k", "hdr",
                      "photograph", "raw", "camera", "lens", "bokeh", "ultra-realistic"],
    "flux-anime":    ["anime", "manga", "chibi", "kawaii", "Studio Ghibli", "cartoon",
                      "illustration", "cel-shaded", "2d"],
    "flux-3d":       ["3d", "render", "cgi", "blender", "cinema4d", "octane", "vray",
                      "unreal engine", "3d render", "isometric"],
    "flux-cablyai":  ["painting", "watercolor", "oil painting", "impressionist",
                      "artistic", "digital art", "concept art", "illustration", "sketch"],
}

# ── Prompt quality boosters per style ─────────────────────────────────────────
_ENHANCERS = {
    "flux":          ", masterpiece, best quality, highly detailed, sharp focus",
    "flux-realism":  ", RAW photo, 8k uhd, DSLR, soft lighting, high quality, film grain",
    "flux-anime":    ", masterpiece, best quality, ultra-detailed, vibrant colors",
    "flux-3d":       ", octane render, 4k, cinematic lighting, subsurface scattering",
    "flux-cablyai":  ", artstation, trending, beautiful composition, vibrant colors",
    "turbo":         "",
}

# ── Gradio fallback spaces ────────────────────────────────────────────────────
_GRADIO_SPACES = [
    ("mukaist/DALLE-4k",       "/run"),
    ("stabilityai/sdxl-turbo", "/predict"),
]


def _detect_model(prompt: str) -> str:
    """Auto-select best Pollinations model based on keywords in the prompt."""
    pl = prompt.lower()
    for model, keywords in _STYLE_KEYWORDS.items():
        if any(kw in pl for kw in keywords):
            return model
    return "flux"  # default


def _enhance_prompt(prompt: str, model: str) -> str:
    """Append quality-boosting keywords appropriate to the chosen model."""
    enhancer = _ENHANCERS.get(model, "")
    return prompt.strip() + enhancer


class AyoubTxt2ImgTool(BaseTool):
    """
    Generate images from a text prompt.
    Primary:  Pollinations.ai (free, no key, 6 FLUX models)
    Fallback: Gradio spaces
    """

    def __init__(
        self,
        description: str = (
            "Generate high-quality images from a text prompt. "
            "Automatically picks the best AI model (realistic, anime, 3D, art). "
            "Saves to output/imgs/ and opens the result."
        ),
        tool_name: str = "image_to_text_tool",
    ):
        super().__init__(description, tool_name)
        OUTPUT_IMGS_DIR.mkdir(parents=True, exist_ok=True)

    def execute_func(self, prompt: str) -> str:
        prompt = prompt.strip().splitlines()[0]  # take first line only

        model   = _detect_model(prompt)
        enhanced = _enhance_prompt(prompt, model)

        print(f"\n[image_gen] Model    : {model}")
        print(f"[image_gen] Prompt   : {prompt[:80]}")
        print(f"[image_gen] Enhanced : {enhanced[:80]}...")
        print(f"[image_gen] Generating via Pollinations.ai ...")

        # ── Primary: Pollinations ─────────────────────────────────────────────
        result = self._pollinations(enhanced, model)
        if result:
            return result

        # ── Fallback: Gradio ─────────────────────────────────────────────────
        print("[image_gen] Pollinations failed — trying Gradio spaces ...")
        return self._gradio_fallback(prompt)

    # ── Pollinations.ai ───────────────────────────────────────────────────────

    def _pollinations(self, prompt: str, model: str) -> str:
        try:
            from urllib.parse import quote
            encoded = quote(prompt)
            url = (
                f"https://image.pollinations.ai/prompt/{encoded}"
                f"?width={_DEFAULT_WIDTH}&height={_DEFAULT_HEIGHT}"
                f"&model={model}&nologo=true&enhance=true&seed={int(time.time())}"
            )
            print(f"[image_gen] Requesting: {url[:80]}...")

            resp = requests.get(url, timeout=_TIMEOUT, stream=True)
            if resp.status_code != 200:
                print(f"[image_gen] HTTP {resp.status_code}")
                return ""

            # Content-Type should be image/*
            ct = resp.headers.get("content-type", "")
            if "image" not in ct:
                print(f"[image_gen] Unexpected content-type: {ct}")
                return ""

            # Save
            ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = OUTPUT_IMGS_DIR / f"ayoub_{model}_{ts}.png"
            path.write_bytes(resp.content)

            print(f"[image_gen] Saved: {path}")
            self._open_image(path)

            return (
                f"Image generated successfully!\n"
                f"  Model   : {model}\n"
                f"  Saved to: {path}\n"
                f"  Size    : {len(resp.content) // 1024} KB"
            )
        except Exception as exc:
            print(f"[image_gen] Pollinations error: {exc}")
            return ""

    # ── Gradio fallback ───────────────────────────────────────────────────────

    def _gradio_fallback(self, prompt: str) -> str:
        try:
            from gradio_client import Client
        except ImportError:
            return "[image_gen] gradio_client not installed."

        last_err = ""
        for space, api_name in _GRADIO_SPACES:
            try:
                print(f"[image_gen] Trying Gradio space: {space}")
                client = Client(space)
                result = client.predict(prompt, api_name=api_name)

                if isinstance(result, list) and result and isinstance(result[0], list):
                    img_dirs = [r["image"] for r in result[0] if isinstance(r, dict)]
                elif isinstance(result, list):
                    img_dirs = [r for r in result if isinstance(r, str)]
                else:
                    img_dirs = [str(result)]

                if not img_dirs:
                    continue

                ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
                saved = []
                for i, src in enumerate(img_dirs):
                    dst = OUTPUT_IMGS_DIR / f"ayoub_gradio_{ts}_{i}.png"
                    import shutil
                    shutil.copy2(src, dst)
                    saved.append(str(dst))

                self._open_image(Path(saved[0]))
                return f"Image saved via {space}: {', '.join(saved)}"
            except Exception as exc:
                last_err = f"[{space}] {exc}"
                continue

        return f"[image_gen] All sources failed. Last error: {last_err}"

    # ── Open image ────────────────────────────────────────────────────────────

    def _open_image(self, path: Path) -> None:
        """Open generated image for the user to see."""
        try:
            import subprocess, sys
            if sys.platform.startswith("win"):
                os.startfile(str(path))
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception:
            pass  # Not critical


class AyoubSketch2ImgTool(BaseTool):
    """Open a sketch canvas, turn your drawing into an AI image."""

    def __init__(
        self,
        description: str = "Open a drawing canvas, sketch something, then refine it into an AI-generated image",
        tool_name: str = "sketch_to_image_tool",
    ):
        super().__init__(description, tool_name)
        OUTPUT_SKETCHES.mkdir(parents=True, exist_ok=True)

    def execute_func(self, prompt: str) -> str:
        try:
            from gradio_client import Client
            from helpers.sketch_window import sketch_window

            img_path = sketch_window()

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

            ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
            dst = OUTPUT_SKETCHES / f"sketch_{ts}.png"
            import shutil
            shutil.copy2(result[0], dst)

            return f"Sketch image saved to: {dst}"
        except Exception as exc:
            return f"[sketch_to_image_tool] Error: {exc}"
