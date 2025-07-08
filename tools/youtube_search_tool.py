from __future__ import annotations

import os
from typing import List, Optional

from pydantic import BaseModel
from googleapiclient.discovery import build

from agents.tool import function_tool


class VideoResult(BaseModel):
    """Video metadata returned from the YouTube Data API."""

    url: str
    title: Optional[str] | None = None
    author: Optional[str] | None = None
    channel: Optional[str] | None = None
    view_count: Optional[int] | None = None
    published_at: Optional[str] | None = None


def _get_client():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY environment variable not set")
    return build("youtube", "v3", developerKey=api_key)


@function_tool(
    name_override="youtube_search",
    description_override="Search YouTube videos using the official YouTube Data API",
)
def youtube_search(
    query: str,
    max_results: int = 5,
    channel_id: Optional[str] = None,
    videoCategoryId: Optional[str] = None,
    order: Optional[str] = None,
) -> List[VideoResult]:
    """Return a list of YouTube videos matching the search query."""

    youtube = _get_client()

    search_kwargs = {
        "part": "id",
        "q": query,
        "maxResults": max_results,
        "type": "video",
    }
    if channel_id:
        search_kwargs["channelId"] = channel_id
    if videoCategoryId:
        search_kwargs["videoCategoryId"] = videoCategoryId
    if order:
        search_kwargs["order"] = order

    search_resp = youtube.search().list(**search_kwargs).execute()
    video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]
    if not video_ids:
        return []

    videos_resp = (
        youtube.videos()
        .list(part="snippet,statistics", id=",".join(video_ids))
        .execute()
    )

    results: List[VideoResult] = []
    for item in videos_resp.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        results.append(
            VideoResult(
                url=f"https://www.youtube.com/watch?v={item['id']}",
                title=snippet.get("title"),
                author=snippet.get("channelTitle"),
                channel=snippet.get("channelTitle"),
                view_count=int(stats.get("viewCount")) if stats.get("viewCount") else None,
                published_at=snippet.get("publishedAt"),
            )
        )

    return results
