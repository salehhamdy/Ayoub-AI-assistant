"""
ayoub/mcp_server/tools/web.py — Web tools for the MCP server.

Ported from friday-tony-stark-demo/friday/tools/web.py
"""
import asyncio
from ayoub.tools.web_tools import (
    get_world_news as _get_world_news,
    fetch_url as _fetch_url,
    open_world_monitor,
    open_urls_in_browser,
)


def register(mcp) -> None:
    """Register all web tools on the FastMCP instance."""

    @mcp.tool()
    async def get_world_news() -> str:
        """Fetch top world news headlines from BBC, CNBC, NYT and Al-Jazeera."""
        return await _get_world_news()

    @mcp.tool()
    async def fetch_url(url: str) -> str:
        """Fetch the raw text content of a URL (first 4000 characters)."""
        return await _fetch_url(url)

    @mcp.tool()
    def search_web(query: str) -> str:
        """Search the internet for a query, open result pages in the browser, and return the top result text."""
        from ayoub.tools.search_tool import AyoubSearchTool
        tool = AyoubSearchTool()
        # Run the search
        result_text = tool.execute_func(query)
        # Extract URLs from the results and open them in the browser
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                hits = list(ddgs.text(query, max_results=3))
            urls = [h.get("href", "") for h in hits if h.get("href")]
            open_urls_in_browser(urls)
        except Exception:
            pass
        return result_text

    @mcp.tool()
    def open_world_monitor_tool() -> str:
        """Open the World Monitor website in the default browser."""
        return open_world_monitor()
