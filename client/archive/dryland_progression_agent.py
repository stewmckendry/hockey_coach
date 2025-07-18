from __future__ import annotations

"""Agent to craft the seasonal progression overview."""

import argparse
import asyncio
from pathlib import Path
from pydantic import BaseModel
from agents import Agent, Runner
from agents.mcp import MCPServerSse

from ..off_ice.dryland_structure_agent import DrylandOutline

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts" / "off_ice"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


class DrylandProgression(BaseModel):
    progression: str


dryland_progression_agent = Agent(
    name="DrylandProgressionAgent",
    instructions=_load_prompt("progression_prompt.yaml"),
    output_type=DrylandProgression,
    mcp_servers=[MCPServerSse(name="Off-Ice KB MCP Server", params={"url": "http://localhost:8000/sse", "timeout": 30})],
    model="gpt-4o",
)


async def run_agent(outline: DrylandOutline) -> DrylandProgression:
    res = await Runner.run(dryland_progression_agent, outline.model_dump_json())
    return res.final_output_as(DrylandProgression)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="Outline JSON")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dryland_progression.json"),
        help="Where to save progression JSON",
    )
    args = parser.parse_args()

    outline = DrylandOutline.model_validate_json(args.input.read_text())
    prog = asyncio.run(run_agent(outline))
    args.output.write_text(prog.model_dump_json(indent=2), encoding="utf-8")
    print(f"✅ Dryland progression saved to {args.output}")


if __name__ == "__main__":
    main()
