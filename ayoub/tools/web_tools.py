"""
ayoub/tools/web_tools.py — Async web tools: news, fetch, world monitor.

Ported from friday-tony-stark-demo/friday/tools/web.py
Uses webbrowser.open() for cross-platform browser opening (no google-chrome).
"""
import asyncio
import re
import webbrowser
import xml.etree.ElementTree as ET

import httpx

_RSS_FEEDS = [
    ("BBC",        "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("CNBC",       "https://www.cnbc.com/id/100727362/device/rss/rss.html"),
    ("NYT",        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    ("Al-Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
]

_HEADERS = {"User-Agent": "Ayoub-AI/1.0"}


async def _fetch_feed(client: httpx.AsyncClient, source: str, url: str) -> list:
    try:
        r = await client.get(url, headers=_HEADERS, timeout=6.0)
        if r.status_code != 200:
            return []
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall(".//item")[:5]:
            title = item.findtext("title") or ""
            desc  = re.sub(r"<[^>]+>", "", item.findtext("description") or "").strip()
            link  = item.findtext("link") or ""
            items.append({
                "source": source,
                "title":  title,
                "summary": desc[:200] + ("..." if len(desc) > 200 else ""),
                "link":   link,
            })
        return items
    except Exception:
        return []


async def get_world_news() -> str:
    """Fetch top headlines from BBC, CNBC, NYT and Al-Jazeera in parallel."""
    async with httpx.AsyncClient(follow_redirects=True) as client:
        results = await asyncio.gather(
            *[_fetch_feed(client, src, url) for src, url in _RSS_FEEDS]
        )
    articles = [a for sub in results for a in sub]
    if not articles:
        return "Unable to reach news feeds right now, sir."

    lines = ["### GLOBAL NEWS BRIEFING\n"]
    for a in articles[:12]:
        lines += [
            f"**[{a['source']}]** {a['title']}",
            a["summary"],
            f"Link: {a['link']}\n",
        ]
    return "\n".join(lines)


async def fetch_url(url: str) -> str:
    """Fetch raw text from a URL (first 4000 characters)."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        r = await client.get(url, headers=_HEADERS)
        return r.text[:4000]


def open_world_monitor() -> str:
    """Open worldmonitor.app in the system default browser (cross-platform)."""
    webbrowser.open("https://worldmonitor.app/")
    return "World Monitor opened in your browser, sir."
