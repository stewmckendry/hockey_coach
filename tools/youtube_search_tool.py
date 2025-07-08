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


def _resolve_channel_id(channel: str) -> str:
    """Return channel ID from handle or URL."""
    youtube = _get_client()
    if channel.startswith("UC"):
        return channel
    if channel.startswith("http"):
        # attempt to parse /channel/ID or /@handle
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
    # fallback search by query
    resp = (
        youtube.search()
        .list(q=channel, type="channel", part="snippet", maxResults=1)
        .execute()
    )
    items = resp.get("items", [])
    if not items:
        raise ValueError(f"Unable to resolve channel id for {channel}")
    return items[0]["snippet"]["channelId"]


def fetch_channel_videos(
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
    remaining = limit
    while True:
        if next_page:
            search_kwargs["pageToken"] = next_page
        resp = youtube.search().list(**search_kwargs).execute()
        ids = [it["id"]["videoId"] for it in resp.get("items", [])]
        if not ids:
            break

        vid_resp = (
            youtube.videos()
            .list(part="snippet,statistics", id=",".join(ids))
            .execute()
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
        if not next_page or (limit and remaining and len(videos) >= limit):
            break

    return videos


def get_video_metadata(video_id: str) -> VideoResult:
    """Fetch metadata for a single video."""
    youtube = _get_client()
    resp = (
        youtube.videos()
        .list(part="snippet,statistics", id=video_id)
        .execute()
    )
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

