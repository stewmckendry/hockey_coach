"""Video search agent using WebSearchTool to find YouTube clips."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from agents import Agent, Runner
from agents.tool import WebSearchTool, function_tool

import yt_dlp


# --- Channel tool -----------------------------------------------------------
@function_tool(name_override="youtube_channel_videos", description_override="Fetch video URLs from a YouTube channel")
def youtube_channel_videos(channel_url: str, limit: Optional[int] = None) -> List[str]:
    """Return a list of video URLs from the given YouTube channel."""
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)

    entries = info.get("entries", []) or []
    urls: List[str] = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        url = e.get("url")
        if url and not url.startswith("http"):
            url = f"https://www.youtube.com/watch?v={e.get('id')}"
        if url:
            urls.append(url)
    if limit:
        urls = urls[:limit]
    return urls


# --- Output schema ---------------------------------------------------------
class VideoResult(BaseModel):
    url: str
    title: Optional[str] | None = None


class VideoSearchResults(BaseModel):
    videos: List[VideoResult]


# --- Prompt loader ---------------------------------------------------------
def _load_prompt() -> str:
    path = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "video_search_prompt.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


# --- Agent -----------------------------------------------------------------
video_search_agent = Agent(
    name="VideoSearchAgent",
    instructions=_load_prompt(),
    tools=[WebSearchTool(), youtube_channel_videos],
    output_type=VideoSearchResults,
)


# --- CLI -------------------------------------------------------------------
def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Search YouTube videos with the VideoSearchAgent")
    parser.add_argument("--query", required=True, help="Search query text")
    parser.add_argument("--num", type=int, default=10, help="Number of videos to request")
    parser.add_argument("--output", type=Path, default=Path("data/input/websearch_results.txt"), help="Output file (.txt or .json)")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable not set")

    query = args.query
    if "site:youtube.com" not in query:
        query += " site:youtube.com"
    query += f" num:{args.num}"

    result = Runner.run_sync(video_search_agent, query)
    output = result.final_output_as(VideoSearchResults)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix == ".json":
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump([v.model_dump() for v in output.videos], f, indent=2)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            for v in output.videos:
                f.write(v.url + "\n")
    print(f"✅ Saved {len(output.videos)} video links to {args.output}")


if __name__ == "__main__":
    run_cli()
