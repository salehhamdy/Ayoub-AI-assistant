"""
ayoub/mcp_server/tools/utils.py — Utility tools for the MCP server.
"""
import json


def register(mcp) -> None:
    """Register utility tools on the FastMCP instance."""

    @mcp.tool()
    def format_json(data: str) -> str:
        """Pretty-print a JSON string. Returns formatted JSON or an error message."""
        try:
            parsed = json.loads(data)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as exc:
            return f"[format_json] Invalid JSON: {exc}"

    @mcp.tool()
    def word_count(text: str) -> str:
        """Return the word count of the provided text."""
        count = len(text.split())
        return f"{count} words"
