"""Video search agent using the YouTube Data API to find clips."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from agents import Agent, Runner
from agents.tool import function_tool
from tools.youtube_search_tool import youtube_search, VideoResult

import yt_dlp


# --- Channel tool -----------------------------------------------------------
@function_tool(
    name_override="youtube_channel_videos",
    description_override="Fetch video URLs from a YouTube channel",
)
def youtube_channel_videos(
    channel: str,
    limit: Optional[int] = None,
    sort: Optional[str] = None,
    keywords: Optional[List[str]] = None,
) -> List[str]:
    """Return a list of video URLs from a YouTube channel.

    ``channel`` may be a full URL or just the channel handle.
    The ``sort`` option accepts ``"popular"`` or ``"recent"``.
    ``keywords`` filters videos whose titles contain any of the terms.
    """
    if not channel.startswith("http"):
        channel_url = f"https://www.youtube.com/@{channel}/videos"
    else:
        channel_url = channel
        if "/videos" not in channel_url:
            channel_url = channel_url.rstrip("/") + "/videos"

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)

    entries = info.get("entries", []) or []
    videos = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        url = e.get("url")
        if url and not url.startswith("http"):
            url = f"https://www.youtube.com/watch?v={e.get('id')}"
        videos.append(
            {
                "title": e.get("title", ""),
                "url": url,
                "view_count": e.get("view_count"),
                "published_date": e.get("upload_date")
                or e.get("release_date")
                or e.get("timestamp"),
            }
        )

    if keywords:
        videos = [
            v
            for v in videos
            if any(k.lower() in v.get("title", "").lower() for k in keywords)
        ]

    if sort == "recent":
        videos.sort(key=lambda v: v.get("published_date") or "", reverse=True)
    elif sort == "popular":
        videos.sort(key=lambda v: v.get("view_count") or 0, reverse=True)

    if limit:
        videos = videos[:limit]

    return [v["url"] for v in videos if v.get("url")]


# --- Output schema ---------------------------------------------------------
class VideoSearchResults(BaseModel):
    videos: List[VideoResult]


# --- Prompt loader ---------------------------------------------------------
def _load_prompt() -> str:
    path = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "prompts"
        / "video_search_prompt.yaml"
    )
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


# --- Agent -----------------------------------------------------------------
video_search_agent = Agent(
    name="VideoSearchAgent",
    instructions=_load_prompt(),
    tools=[youtube_search, youtube_channel_videos],
    output_type=VideoSearchResults,
)


# --- CLI -------------------------------------------------------------------
def run_cli() -> None:
    parser = argparse.ArgumentParser(
        description="Search YouTube videos with the VideoSearchAgent"
    )
    parser.add_argument("--query", required=True, help="Search query text")
    parser.add_argument(
        "--num", type=int, default=10, help="Number of videos to request"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/video_index.json"),
        help="Output JSON file for indexed videos",
    )
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    if not os.getenv("YOUTUBE_API_KEY"):
        raise RuntimeError("YOUTUBE_API_KEY environment variable not set")

    query = f"{args.query} num:{args.num}"

    result = Runner.run_sync(video_search_agent, query)
    output = result.final_output_as(VideoSearchResults)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump([v.model_dump() for v in output.videos], f, indent=2)
    print(f"✅ Saved {len(output.videos)} video results to {args.output}")


if __name__ == "__main__":
    run_cli()
