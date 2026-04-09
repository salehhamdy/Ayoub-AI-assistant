"""
ayoub/tools/scrape_tool.py — URL scraper using BeautifulSoup.

Ported from hereiz customAgents/agent_tools/search_tool.py (scrape helper).
Cross-platform: pure Python requests.
"""
import random
import requests
from bs4 import BeautifulSoup

from ayoub.agent.toolkit import BaseTool

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Firefox/121",
]


class AyoubScrapeTool(BaseTool):
    """Fetches and returns plain text from a URL."""

    def __init__(
        self,
        description: str = "Scrape and return the text content of a webpage given its URL",
        tool_name: str = "scrape_tool",
        max_num_chars: int = 10_000,
        timeout: int = 10,
    ):
        super().__init__(description, tool_name)
        self.max_num_chars = max_num_chars
        self.timeout = timeout

    def execute_func(self, url: str) -> str:
        url = url.strip()
        if not url.startswith("http"):
            return f"[scrape_tool] Invalid URL: {url}"
        try:
            headers = {"User-Agent": random.choice(_USER_AGENTS)}
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            soup = BeautifulSoup(resp.text, "lxml")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
            return text[: self.max_num_chars]
        except Exception as exc:
            return f"[scrape_tool] Error: {exc}"
