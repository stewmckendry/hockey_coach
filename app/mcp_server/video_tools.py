"""MCP tools for searching YouTube videos."""

from __future__ import annotations
from typing import List, Optional

from .server import mcp
from tools.youtube_search_tool import (
    youtube_search as _youtube_search,
    fetch_channel_videos as _fetch_channel_videos,
    VideoResult,
)


@mcp.tool(title="Search YouTube Videos")
def search_youtube_videos(query: str, max_results: int = 5) -> List[VideoResult]:
    """Search YouTube videos."""
    return _youtube_search(query=query, max_results=max_results)


@mcp.tool(title="Fetch Channel Videos")
def fetch_channel_videos(
    channel_id: str,
    sort: Optional[str] = None,
    limit: Optional[int] = None,
    keywords: Optional[List[str]] = None,
) -> List[VideoResult]:
    """Fetch videos from a specific YouTube channel."""
    return _fetch_channel_videos(channel=channel_id, limit=limit, sort=sort, keywords=keywords)
