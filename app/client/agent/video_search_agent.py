"""Video search agent using the YouTube Data API to find clips."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import List, Optional
import asyncio


def _slugify(text: str) -> str:
    """Return a filename-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")

from pydantic import BaseModel

from agents import Agent, Runner
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings
from app.mcp_server.video_tools import VideoResult




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
    output_type=VideoSearchResults,
    mcp_servers=[MCPServerSse(name="Thunder Video Search", params={"url": "http://localhost:8000/sse"})],
    model="gpt-4o",
    model_settings=ModelSettings(tool_choice="required"),
)


# --- CLI -------------------------------------------------------------------
async def run_cli() -> None:
    parser = argparse.ArgumentParser(
        description="Search YouTube videos with the VideoSearchAgent"
    )
    parser.add_argument("--query", help="Search query text")
    parser.add_argument(
        "--query-file",
        type=Path,
        help="File containing search queries, one per line",
    )
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

    if not args.query and not args.query_file:
        parser.error("Provide --query or --query-file")

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable not set")

    mcp_server = video_search_agent.mcp_servers[0]
    await mcp_server.connect()

    tasks = []
    outputs: list[tuple[str, Path]] = []

    if args.query:
        outputs.append((args.query, args.output))

    if args.query_file:
        prefix = "video_search_dryland_" if "dryland" in args.query_file.stem else "video_search_"
        with open(args.query_file, "r", encoding="utf-8") as f:
            for ln in f:
                q = ln.strip()
                if not q:
                    continue
                slug = _slugify(q)
                out_path = args.query_file.parent / f"{prefix}{slug}.json"
                outputs.append((q, out_path))

    for q, out_path in outputs:
        query = f"{q} num:{args.num}"
        result = await Runner.run(video_search_agent, query)
        output = result.final_output_as(VideoSearchResults)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump([v.model_dump() for v in output.videos], f, indent=2)
        print(f"✅ Saved {len(output.videos)} videos for \"{q}\" -> {out_path.name}")



if __name__ == "__main__":
    import asyncio
    asyncio.run(run_cli())
