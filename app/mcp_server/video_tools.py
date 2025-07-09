"""MCP tools for searching YouTube videos."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel
from googleapiclient.discovery import build

from .server import mcp

DEBUG = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes"}


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


def _soften_query(query: str) -> str:
    soften_words = {"top", "best"}
    parts = [p for p in query.split() if p.lower() not in soften_words]
    return " ".join(parts) or query


def _youtube_search(
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
        "order": order or "viewCount",
    }
    if channel_id:
        search_kwargs["channelId"] = channel_id
    if videoCategoryId:
        search_kwargs["videoCategoryId"] = videoCategoryId

    def _execute_search(**kwargs) -> List[VideoResult]:
        resp = youtube.search().list(**kwargs).execute()
        ids = [item["id"]["videoId"] for item in resp.get("items", [])]
        if not ids:
            return []
        video_resp = (
            youtube.videos().list(part="snippet,statistics", id=",".join(ids)).execute()
        )
        results: List[VideoResult] = []
        for item in video_resp.get("items", []):
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

    results = _execute_search(**search_kwargs)
    if DEBUG:
        print(f"🔍 YouTube API query='{query}' returned {len(results)} results")

    if not results:
        # retry with softened query
        soft_query = _soften_query(query)
        if soft_query != query:
            search_kwargs["q"] = soft_query
            results = _execute_search(**search_kwargs)
            if DEBUG:
                print(
                    f"🔍 retry softened query='{soft_query}' returned {len(results)} results"
                )
    if not results:
        # last resort: search only videos in last year
        search_kwargs["q"] = query
        search_kwargs["publishedAfter"] = (
            datetime.utcnow() - timedelta(days=365)
        ).isoformat("T") + "Z"
        results = _execute_search(**search_kwargs)
        if DEBUG:
            print(
                f"🔍 retry with publishedAfter returned {len(results)} results"
            )

    return results


def _resolve_channel_id(channel: str) -> str:
    """Return channel ID from handle or URL."""
    youtube = _get_client()
    if channel.startswith("UC"):
        return channel
    if channel.startswith("http"):
        try:
            from urllib.parse import urlparse

            parsed = urlparse(channel)
            parts = [p for p in parsed.path.split("/") if p]
            if "channel" in parts:
                idx = parts.index("channel")
                if idx + 1 < len(parts):
                    return parts[idx + 1]
            for part in parts:
                if part.startswith("@"):  # handle
                    channel = part
                    break
        except Exception:
            pass
    if channel.startswith("@"):  # handle
        handle = channel.lstrip("@")
        resp = (
            youtube.search()
            .list(q=handle, type="channel", part="snippet", maxResults=1)
            .execute()
        )
        items = resp.get("items", [])
        if items:
            return items[0]["snippet"]["channelId"]
    resp = (
        youtube.search()
        .list(q=channel, type="channel", part="snippet", maxResults=1)
        .execute()
    )
    items = resp.get("items", [])
    if not items:
        raise ValueError(f"Unable to resolve channel id for {channel}")
    return items[0]["snippet"]["channelId"]


def _fetch_channel_videos(
    channel: str,
    limit: int | None = None,
    sort: str | None = None,
    keywords: List[str] | None = None,
) -> List[VideoResult]:
    """Return videos from a channel using the YouTube Data API."""
    youtube = _get_client()
    channel_id = _resolve_channel_id(channel)

    order = None
    if sort == "recent":
        order = "date"
    elif sort == "popular":
        order = "viewCount"

    search_kwargs = {
        "part": "id",
        "channelId": channel_id,
        "maxResults": min(limit or 50, 50),
        "type": "video",
    }
    if order:
        search_kwargs["order"] = order

    videos: List[VideoResult] = []
    next_page = None
    while True:
        if next_page:
            search_kwargs["pageToken"] = next_page
        resp = youtube.search().list(**search_kwargs).execute()
        ids = [it["id"]["videoId"] for it in resp.get("items", [])]
        if not ids:
            break

        vid_resp = (
            youtube.videos().list(part="snippet,statistics", id=",".join(ids)).execute()
        )
        for item in vid_resp.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            title = snippet.get("title", "")
            if keywords and not any(k.lower() in title.lower() for k in keywords):
                continue
            videos.append(
                VideoResult(
                    url=f"https://www.youtube.com/watch?v={item['id']}",
                    title=title,
                    author=snippet.get("channelTitle"),
                    channel=snippet.get("channelTitle"),
                    view_count=int(stats.get("viewCount")) if stats.get("viewCount") else None,
                    published_at=snippet.get("publishedAt"),
                )
            )

        if limit and len(videos) >= limit:
            videos = videos[:limit]
            break

        next_page = resp.get("nextPageToken")
        if not next_page:
            break

    if DEBUG:
        print(
            f"📺 fetch_channel_videos collected {len(videos)} videos from '{channel}'"
        )
    return videos


def get_video_metadata(video_id: str) -> VideoResult:
    """Fetch metadata for a single video."""
    youtube = _get_client()
    resp = youtube.videos().list(part="snippet,statistics", id=video_id).execute()
    items = resp.get("items", [])
    if not items:
        raise ValueError(f"No video found for id {video_id}")
    item = items[0]
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    return VideoResult(
        url=f"https://www.youtube.com/watch?v={video_id}",
        title=snippet.get("title"),
        author=snippet.get("channelTitle"),
        channel=snippet.get("channelTitle"),
        view_count=int(stats.get("viewCount")) if stats.get("viewCount") else None,
        published_at=snippet.get("publishedAt"),
    )


@mcp.tool(title="Search YouTube Videos")
def search_youtube_videos(query: str, max_results: int = 5) -> List[VideoResult]:
    """Search YouTube videos."""
    results = _youtube_search(query=query, max_results=max_results)
    print(
        f"📺 MCP Tool 'search_youtube_videos' returned {len(results)} videos for '{query}'"
    )
    return results


@mcp.tool(title="Fetch Channel Videos")
def fetch_channel_videos(
    channel_id: str,
    sort: Optional[str] = None,
    limit: Optional[int] = None,
    keywords: Optional[List[str]] = None,
) -> List[VideoResult]:
    """Fetch videos from a specific YouTube channel."""
    results = _fetch_channel_videos(channel=channel_id, limit=limit, sort=sort, keywords=keywords)
    print(
        f"📺 MCP Tool 'fetch_channel_videos' returned {len(results)} videos from '{channel_id}'"
    )
    return results
