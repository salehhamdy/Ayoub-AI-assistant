"""
ayoub/tools/search_tool.py — DuckDuckGo web search tool.

Ported from hereiz customAgents/agent_tools/search_tool.py
Cross-platform: pure Python requests + BeautifulSoup, no shell commands.
"""
import random
import requests
from bs4 import BeautifulSoup

from ayoub.agent.toolkit import BaseTool
from ayoub.config import SEARCH_HISTORY

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
]


class AyoubSearchTool(BaseTool):
    """
    Searches the web via DuckDuckGo HTML interface.
    Returns scraped page text from the top result(s).
    """

    def __init__(
        self,
        description: str = "Search the internet for information on any topic using DuckDuckGo",
        tool_name: str = "search_tool",
        max_num_chars: int = 5000,
        num_top_results: int = 1,
        save_history: bool = True,
        request_timeout: int = 10,
    ):
        super().__init__(description, tool_name)
        self.max_num_chars = max_num_chars
        self.num_top_results = num_top_results
        self.save_history = save_history
        self.request_timeout = request_timeout

    def execute_func(self, query: str) -> str:
        results = self._ddg_search(query.strip())
        if not results:
            return "[search_tool] No results found."

        if self.save_history:
            self._save_history(query, results)

        combined = ""
        for r in results[: self.num_top_results]:
            text = self._scrape(r["link"])
            combined += f"\n[Source: {r['link']}]\n{text}\n"

        return combined[: self.max_num_chars]

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _ddg_search(self, query: str) -> list:
        url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"
        headers = {"User-Agent": random.choice(_USER_AGENTS)}
        try:
            resp = requests.get(url, headers=headers, timeout=self.request_timeout)
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            for a in soup.find_all("a", {"class": "result__url"}):
                link = a.get("href", "")
                results.append({"title": a.get_text(strip=True), "link": link})
            return results
        except Exception as exc:
            return [{"title": "Error", "link": f"[Search failed: {exc}]"}]

    def _scrape(self, url: str) -> str:
        if not url.startswith("http"):
            return f"[Invalid URL: {url}]"
        try:
            headers = {"User-Agent": random.choice(_USER_AGENTS)}
            resp = requests.get(url, headers=headers, timeout=self.request_timeout)
            soup = BeautifulSoup(resp.text, "lxml")
            # Remove script/style noise
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            return soup.get_text(separator=" ", strip=True)
        except Exception as exc:
            return f"[Scrape error: {exc}]"

    def _save_history(self, query: str, results: list) -> None:
        try:
            SEARCH_HISTORY.parent.mkdir(parents=True, exist_ok=True)
            with SEARCH_HISTORY.open("a", encoding="utf-8") as f:
                f.write(f"\nQuery: {query}\n")
                for r in results[: self.num_top_results]:
                    f.write(f"  Link: {r['link']}\n")
        except Exception:
            pass  # History saving is non-critical
