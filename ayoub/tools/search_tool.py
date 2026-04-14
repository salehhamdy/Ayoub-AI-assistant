"""
ayoub/tools/search_tool.py — Web search using duckduckgo-search (DDGS).

Uses the `duckduckgo-search` Python package which bypasses bot detection
and returns clean, real URLs with titles and snippets.

Install: pip install duckduckgo-search
"""
import re
import time

import requests
from bs4 import BeautifulSoup

from ayoub.agent.toolkit import BaseTool
from ayoub.config import SEARCH_HISTORY

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}


class AyoubSearchTool(BaseTool):
    """
    Searches the web via DuckDuckGo (duckduckgo-search package).
    Returns titles, URLs, and scraped content from the top results.
    """

    def __init__(
        self,
        description: str = "Search the internet for information on any topic using DuckDuckGo",
        tool_name: str = "search_tool",
        max_num_chars: int = 6000,
        num_top_results: int = 3,
        save_history: bool = True,
        request_timeout: int = 15,
    ):
        super().__init__(description, tool_name)
        self.max_num_chars = max_num_chars
        self.num_top_results = num_top_results
        self.save_history = save_history
        self.request_timeout = request_timeout

    def execute_func(self, query: str) -> str:
        # Strip the LLM's inline comments ("(Note: ...)"  etc.)
        query = re.sub(r"\(.*?\)", "", query).strip().splitlines()[0].strip()

        print(f"\n[search_tool] Searching: {query!r}")

        results = self._ddg_search(query)
        if not results:
            return f"[search_tool] No results found for: {query!r}"

        if self.save_history:
            self._save_history(query, results)

        combined = ""
        for r in results[: self.num_top_results]:
            url   = r.get("href", "")
            title = r.get("title", url)
            body  = r.get("body", "")   # DDGS provides a snippet

            print(f"[search_tool] >> {title[:60]}  ->  {url}")

            # Supplement with a real scrape if snippet is short
            scraped = self._scrape(url) if len(body) < 300 else body

            combined += (
                f"\n[Source: {url}]\n"
                f"[Title: {title}]\n"
                f"{scraped[:1800]}\n"
            )

        return (combined or "[search_tool] Pages found but content could not be extracted.")[: self.max_num_chars]

    # ── DuckDuckGo proper API ─────────────────────────────────────────────────

    def _ddg_search(self, query: str) -> list:
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.num_top_results + 2))
            return results
        except Exception as exc:
            print(f"[search_tool] DDGS error: {exc}")
            return []

    # ── Scraper ───────────────────────────────────────────────────────────────

    def _scrape(self, url: str) -> str:
        if not url.startswith("http"):
            return f"[Invalid URL: {url}]"
        try:
            resp = requests.get(
                url, headers=_HEADERS,
                timeout=self.request_timeout,
                allow_redirects=True,
            )
            if resp.status_code != 200:
                return f"[HTTP {resp.status_code}]"

            soup = BeautifulSoup(resp.text, "lxml")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()

            text = soup.get_text(separator=" ", strip=True)
            text = re.sub(r"\s{3,}", "  ", text)
            return text[:2000]
        except Exception as exc:
            return f"[Scrape error: {exc}]"

    # ── History ───────────────────────────────────────────────────────────────

    def _save_history(self, query: str, results: list) -> None:
        try:
            SEARCH_HISTORY.parent.mkdir(parents=True, exist_ok=True)
            with SEARCH_HISTORY.open("a", encoding="utf-8") as f:
                f.write(f"\nQuery: {query}\n")
                for r in results[: self.num_top_results]:
                    f.write(f"  Link: {r.get('href', '')}\n")
        except Exception:
            pass
