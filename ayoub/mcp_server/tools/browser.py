"""
ayoub/mcp_server/tools/browser.py — MCP tool registration for Playwright browser actions.
"""
from ayoub.tools.browser_tool import (
    browser_navigate,
    browser_click,
    browser_type,
    browser_press_enter,
    browser_read_page,
    browser_scroll,
    browser_go_back,
    browser_screenshot,
    browser_get_current_url,
    browser_close,
)


def register(mcp) -> None:
    """Register all browser interaction tools on the FastMCP instance."""

    @mcp.tool()
    async def navigate_to(url: str) -> str:
        """Navigate the browser to a URL and return the page title and text content."""
        return await browser_navigate(url)

    @mcp.tool()
    async def click_on(target: str) -> str:
        """Click a button, link, or element on the current page by its visible text or CSS selector."""
        return await browser_click(target)

    @mcp.tool()
    async def type_into(selector: str, text: str) -> str:
        """Type text into an input field identified by its placeholder text or CSS selector."""
        return await browser_type(selector, text)

    @mcp.tool()
    async def press_enter() -> str:
        """Press Enter on the currently focused element — useful for submitting forms or searches."""
        return await browser_press_enter()

    @mcp.tool()
    async def read_current_page() -> str:
        """Read and return the visible text content of the currently loaded web page."""
        return await browser_read_page()

    @mcp.tool()
    async def scroll_page(direction: str = "down") -> str:
        """Scroll the current page. direction must be 'up' or 'down'."""
        return await browser_scroll(direction)

    @mcp.tool()
    async def go_back() -> str:
        """Navigate back to the previous page in browser history."""
        return await browser_go_back()

    @mcp.tool()
    async def take_screenshot() -> str:
        """Take a screenshot of the current browser page and open it on screen."""
        return await browser_screenshot()

    @mcp.tool()
    async def get_current_url() -> str:
        """Return the URL currently loaded in the browser."""
        return await browser_get_current_url()

    @mcp.tool()
    async def close_browser() -> str:
        """Close the browser window and release all resources."""
        return await browser_close()
