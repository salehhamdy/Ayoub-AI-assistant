"""
ayoub/mcp_server/server.py — FastMCP tool server.

Ported from friday-tony-stark-demo/server.py
Exposes all tools over Server-Sent Events (SSE) on port 8000.

Usage:
    ayoub-server          # from CLI after uv sync
    python -m ayoub.mcp_server.server
"""
from fastmcp import FastMCP
from ayoub.config import MCP_SERVER_PORT
from ayoub.mcp_server.tools import web, system, utils

mcp = FastMCP("Ayoub MCP Server")

# Register all tool groups
web.register(mcp)
system.register(mcp)
utils.register(mcp)


def main() -> None:
    """Entry point for ayoub-server console script."""
    print(f"[Ayoub MCP Server] Starting on port {MCP_SERVER_PORT}...")
    mcp.run(transport="sse", port=MCP_SERVER_PORT)


if __name__ == "__main__":
    main()
