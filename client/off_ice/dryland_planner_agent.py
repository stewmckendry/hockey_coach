from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Optional

from agents import Agent, Runner, WebSearchTool
from agents.mcp import MCPServerSse

from models.dryland_models import DrylandContext, DrylandPlanOutput
from dryland_context_tools import set_dryland_context_param

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts" / "off_ice"


def _load_prompt() -> str:
    path = PROMPTS_DIR / "dryland_plan_prompt.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()

def get_dryland_planner_agent(mcp_servers) -> Agent:
    return Agent(
        name="DrylandPlannerAgent",
        instructions=_load_prompt(),
        #output_type=DrylandPlanOutput, -- commented out to enable multi-turn mode
        tools=[set_dryland_context_param, WebSearchTool()],
        mcp_servers=[mcp_servers],
    )

"""
async def run_agent(context: DrylandContext, *, max_turns: int = 20) -> DrylandPlanOutput:
    res = await Runner.run(dryland_planner_agent, "", context=context, max_turns=max_turns)
    plan = res.final_output_as(DrylandPlanOutput)
    context.plan = plan
    return plan


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", type=Path, help="Optional context JSON")
    parser.add_argument("--output", type=Path, default=Path("dryland_plan.json"))
    args = parser.parse_args()

    ctx = DrylandContext()
    if args.context and args.context.exists():
        ctx = DrylandContext.model_validate_json(args.context.read_text())

    plan = asyncio.run(run_agent(ctx))
    args.output.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    print(f"✅ Plan saved to {args.output}")


if __name__ == "__main__":
    main()
"""