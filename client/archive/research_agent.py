from __future__ import annotations

"""Agent that performs web research to gather quick insights."""

import argparse
import asyncio
from pathlib import Path
from typing import List

from pydantic import BaseModel
from agents import Agent, Runner, WebSearchTool

from ..archive.dryland_progression_agent import DrylandProgression

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts" / "off_ice"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


class ResearchSummary(BaseModel):
    bullets: List[str]


research_agent = Agent(
    name="WorkoutResearcher",
    instructions=_load_prompt("web_prompt.yaml"),
    output_type=ResearchSummary,
    tools=[WebSearchTool()],
    model="gpt-4o",
)


async def run_agent(prog: DrylandProgression) -> ResearchSummary:
    res = await Runner.run(research_agent, prog.model_dump_json(), max_turns=10)
    return res.final_output_as(ResearchSummary)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="Progression JSON")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research_summary.json"),
        help="Where to save research JSON",
    )
    args = parser.parse_args()

    progression = DrylandProgression.model_validate_json(args.input.read_text())
    research = asyncio.run(run_agent(progression))
    args.output.write_text(research.model_dump_json(indent=2), encoding="utf-8")
    print(f"✅ Research summary saved to {args.output}")


if __name__ == "__main__":
    main()
