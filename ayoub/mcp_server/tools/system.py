"""
ayoub/mcp_server/tools/system.py — System tools for the MCP server.

Ported from friday-tony-stark-demo/friday/tools/system.py
"""
from ayoub.tools.system_tools import get_current_time, get_system_info


def register(mcp) -> None:
    """Register system tools on the FastMCP instance."""

    @mcp.tool()
    def get_time() -> str:
        """Return the current date and time in ISO 8601 format."""
        return get_current_time()

    @mcp.tool()
    def system_info() -> dict:
        """Return operating system, version, processor, and Python version info."""
        return get_system_info()
