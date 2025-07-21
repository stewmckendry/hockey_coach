from __future__ import annotations

"""Simple date/time utility tools for MCP."""

from datetime import datetime, timezone
from fastmcp import FastMCP

mcp = FastMCP("Datetime Tools")

@mcp.tool("get_current_date")
def get_current_date(fmt: str = "%Y-%m-%d") -> str:
    """Return the current UTC date formatted as a string."""
    return datetime.now(timezone.utc).strftime(fmt)

if __name__ == "__main__":
    mcp.run(transport="sse")
