"""
ayoub/tools/browser_tool.py — Direct website interaction via Playwright.

Maintains a single persistent headed (visible) Chromium browser so the user
can watch Ayoub control websites in real time.

Install once:
    pip install playwright
    playwright install chromium
"""
from __future__ import annotations

import asyncio
import re
import textwrap
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Lazy singleton — browser is created on first use and reused for the session
# ---------------------------------------------------------------------------
_browser = None          # playwright.async_api.Browser
_context = None          # BrowserContext
_page    = None          # Page
_pw      = None          # Playwright instance
_lock    = asyncio.Lock()


async def _get_page():
    """Return the active page, launching the browser if needed."""
    global _browser, _context, _page, _pw

    async with _lock:
        if _page is not None and not _page.is_closed():
            return _page

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise RuntimeError(
                "Playwright is not installed. Run:\n"
                "  pip install playwright\n"
                "  playwright install chromium"
            )

        _pw      = await async_playwright().start()
        _browser = await _pw.chromium.launch(
            headless=False,          # visible window — user can watch
            args=["--start-maximized"],
        )
        _context = await _browser.new_context(
            viewport=None,           # use window size instead of fixed viewport
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        _page = await _context.new_page()
        return _page


def _clean_text(raw: str, max_chars: int = 3000) -> str:
    """Strip excess whitespace from page text and cap length."""
    text = re.sub(r"\s{3,}", "  ", raw).strip()
    return textwrap.shorten(text, width=max_chars, placeholder=" …[truncated]")


# ---------------------------------------------------------------------------
# Public async tool functions
# ---------------------------------------------------------------------------

async def browser_navigate(url: str) -> str:
    """Navigate to a URL and return the page title + visible text.

    Args:
        url: Full URL to navigate to (must start with http/https).
    """
    if not url.startswith("http"):
        url = "https://" + url

    page = await _get_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20_000)
        await page.wait_for_timeout(1500)   # let JS settle
        title = await page.title()
        text  = await page.inner_text("body")
        return f"[Page: {title}]\n{_clean_text(text)}"
    except Exception as exc:
        return f"[browser_navigate error: {exc}]"


async def browser_click(target: str) -> str:
    """Click an element identified by visible text or CSS selector.

    Args:
        target: Visible button/link text (e.g. "Sign in") or a CSS selector.
    """
    page = await _get_page()
    try:
        # Try visible text first, then fall back to CSS selector
        locator = page.get_by_text(target, exact=False).first
        if await locator.count() == 0:
            locator = page.locator(target).first

        await locator.scroll_into_view_if_needed()
        await locator.click(timeout=8_000)
        await page.wait_for_timeout(1200)
        return f"Clicked '{target}'. Now on: {page.url}"
    except Exception as exc:
        return f"[browser_click error: {exc}]"


async def browser_type(selector: str, text: str) -> str:
    """Focus an input field and type text into it.

    Args:
        selector: CSS selector or placeholder text of the input field.
        text:     The text to type.
    """
    page = await _get_page()
    try:
        # Try placeholder attribute first, then CSS selector
        locator = page.get_by_placeholder(selector, exact=False).first
        if await locator.count() == 0:
            locator = page.locator(selector).first

        await locator.click()
        await locator.fill(text)
        return f"Typed '{text}' into '{selector}'."
    except Exception as exc:
        return f"[browser_type error: {exc}]"


async def browser_press_enter() -> str:
    """Press Enter on the currently focused element (e.g. submit a search)."""
    page = await _get_page()
    try:
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1500)
        return f"Pressed Enter. Now on: {page.url}"
    except Exception as exc:
        return f"[browser_press_enter error: {exc}]"


async def browser_read_page() -> str:
    """Return readable text content of the current page."""
    page = await _get_page()
    try:
        title = await page.title()
        text  = await page.inner_text("body")
        return f"[Page: {title} | {page.url}]\n{_clean_text(text)}"
    except Exception as exc:
        return f"[browser_read_page error: {exc}]"


async def browser_scroll(direction: str = "down") -> str:
    """Scroll the page up or down.

    Args:
        direction: 'up' or 'down'.
    """
    page = await _get_page()
    try:
        delta = 600 if direction.lower() == "down" else -600
        await page.mouse.wheel(0, delta)
        await page.wait_for_timeout(500)
        return f"Scrolled {direction}."
    except Exception as exc:
        return f"[browser_scroll error: {exc}]"


async def browser_go_back() -> str:
    """Navigate back to the previous page."""
    page = await _get_page()
    try:
        await page.go_back(wait_until="domcontentloaded", timeout=10_000)
        await page.wait_for_timeout(1000)
        return f"Went back. Now on: {page.url}"
    except Exception as exc:
        return f"[browser_go_back error: {exc}]"


async def browser_screenshot() -> str:
    """Take a screenshot of the current page and open it on screen.

    Saves to a temp file and opens it with the system viewer.
    """
    import subprocess, sys, tempfile
    page = await _get_page()
    try:
        tmp = Path(tempfile.mktemp(suffix=".png", prefix="ayoub_screenshot_"))
        await page.screenshot(path=str(tmp), full_page=False)

        # Open with system viewer
        if sys.platform == "win32":
            subprocess.Popen(["cmd", "/c", "start", "", str(tmp)],
                             creationflags=subprocess.CREATE_NO_WINDOW)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(tmp)])
        else:
            subprocess.Popen(["xdg-open", str(tmp)])

        return f"Screenshot saved and opened: {tmp.name}"
    except Exception as exc:
        return f"[browser_screenshot error: {exc}]"


async def browser_get_current_url() -> str:
    """Return the URL currently loaded in the browser."""
    page = await _get_page()
    try:
        return page.url
    except Exception as exc:
        return f"[browser_get_current_url error: {exc}]"


async def browser_close() -> str:
    """Close the browser window and release all resources."""
    global _browser, _context, _page, _pw
    try:
        if _page and not _page.is_closed():
            await _page.close()
        if _context:
            await _context.close()
        if _browser:
            await _browser.close()
        if _pw:
            await _pw.stop()
        _page = _context = _browser = _pw = None
        return "Browser closed."
    except Exception as exc:
        return f"[browser_close error: {exc}]"
