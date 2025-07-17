from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Optional

from agents import Agent, Runner, WebSearchTool
from agents.mcp import MCPServerSse
from client.off_ice.research.dryland_research_agent import get_dryland_research_agent
from client.off_ice.intake.dryland_intake_agent import get_dryland_intake_agent

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

async def run_agent(context: DrylandContext, mcp_servers: MCPServerSse, *, max_turns: int = 20) -> DrylandPlanOutput:
    intake_agent = get_dryland_intake_agent()
    intake_result = await Runner.run(intake_agent, "", context=context, max_turns=max_turns)
    prev_id = intake_result.id

    if not context.research_complete:
        research_agent = get_dryland_research_agent(mcp_servers)
        research_result = await Runner.run(
            research_agent,
            previous_response_id=intake_result.id,
            context=context,
        )
        prev_id = research_result.id

    planner_agent = get_dryland_planner_agent(mcp_servers)
    res = await Runner.run(planner_agent, previous_response_id=prev_id, context=context)
    plan = res.final_output_as(DrylandPlanOutput)
    context.plan = plan
    return plan
