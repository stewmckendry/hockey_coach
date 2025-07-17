from __future__ import annotations

"""Agent to search and summarize dryland training video clips."""

import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from agents import Agent, Runner
from agents.mcp import MCPServerSse

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts" / "off_ice"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


class VideoSummary(BaseModel):
    markdown: str


dryland_video_summary_agent = Agent(
    name="DrylandVideoSummary",
    instructions=_load_prompt("video_summary_prompt.yaml"),
    output_type=VideoSummary,
    mcp_servers=[MCPServerSse(name="Off-Ice KB MCP Server", params={"url": "http://localhost:8000/sse", "timeout": 30})],
    model="gpt-4o",
)


async def run_agent(query: Optional[str] = None, title: Optional[str] = None) -> VideoSummary:
    payload = json.dumps({"query": query, "title": title})
    res = await Runner.run(dryland_video_summary_agent, payload, max_turns=10)
    return res.final_output_as(VideoSummary)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, help="Search query")
    parser.add_argument("--title", type=str, help="Video title")
    args = parser.parse_args()

    if not args.query and not args.title:
        parser.error("Provide --query or --title")

    summary = asyncio.run(run_agent(args.query, args.title))

    base = Path(__file__).resolve().parents[2] / "data" / "generated"
    base.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1((args.query or args.title).encode("utf-8")).hexdigest()[:8]
    out_path = base / f"dryland_video_summary_{digest}.md"
    out_path.write_text(summary.markdown, encoding="utf-8")
    print(f"✅ Summary saved to {out_path}")


if __name__ == "__main__":
    main()
