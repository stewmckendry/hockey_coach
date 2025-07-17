from __future__ import annotations

"""Input structuring agent for off-ice workout planning."""

import argparse
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List

from pydantic import BaseModel
from agents import Agent, Runner, function_tool

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts" / "off_ice"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


class StructuredInput(BaseModel):
    age_group: str
    sport: str
    start_date: str
    end_date: str
    frequency: str
    goals: List[str]
    location: str
    amenities: List[str]
    preferred_activities: List[str]


@function_tool
def get_current_date() -> str:
    """Return today's date in ISO format."""
    return datetime.now().date().isoformat()


input_structurer_agent = Agent(
    name="WorkoutInputStructurer",
    instructions=_load_prompt("input_prompt.yaml"),
    output_type=StructuredInput,
    tools=[get_current_date],
    model="gpt-4o",
)


async def run_agent(text: str) -> StructuredInput:
    res = await Runner.run(input_structurer_agent, text)
    return res.final_output_as(StructuredInput)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True, help="Workout request text")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("session_input.json"),
        help="Where to save structured JSON",
    )
    args = parser.parse_args()

    data = asyncio.run(run_agent(args.text))
    args.output.write_text(data.model_dump_json(indent=2), encoding="utf-8")
    print(f"✅ Structured input saved to {args.output}")


if __name__ == "__main__":
    main()
