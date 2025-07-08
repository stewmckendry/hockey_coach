"""Video search agent using the YouTube Data API to find clips."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import List, Optional
import asyncio

from pydantic import BaseModel

from agents import Agent, Runner
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings
from tools.youtube_search_tool import VideoResult




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

    mcp_server = video_search_agent.mcp_servers[0]
    await mcp_server.connect()

    query = f"{args.query} num:{args.num}"
    result = await Runner.run(video_search_agent, query)
    output = result.final_output_as(VideoSearchResults)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump([v.model_dump() for v in output.videos], f, indent=2)
    print(f"✅ Saved {len(output.videos)} video results to {args.output}")



if __name__ == "__main__":
    import asyncio
    asyncio.run(run_cli())
