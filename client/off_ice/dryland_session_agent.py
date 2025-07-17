from __future__ import annotations

import argparse
import asyncio
from datetime import date
from pathlib import Path

from agents import Agent, Runner, WebSearchTool
from agents.mcp import MCPServerSse

from models.dryland_models import DrylandContext, DrylandSessionOutput
from dryland_context_tools import set_dryland_context_param

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts" / "off_ice"


def _load_prompt() -> str:
    path = PROMPTS_DIR / "dryland_session_prompt.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()

def get_dryland_session_agent(mcp_server) -> Agent:
    return Agent(
        name="DrylandSessionAgent",
        instructions=_load_prompt(),
        #output_type=DrylandSessionOutput,-- commented out to enable multi-turn mode
        tools=[set_dryland_context_param, WebSearchTool()],
        mcp_servers=[mcp_server],
        model="gpt-4o",
    )

"""
async def run_agent(session_date: date, context: DrylandContext, *, max_turns: int = 20) -> DrylandSessionOutput:
    await mcp_server.connect()
    print("🏒 Dryland Session")
    res = await Runner.run(dryland_session_agent, session_date.isoformat(), context=context, max_turns=max_turns)
    return res.final_output_as(DrylandSessionOutput)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, required=True)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("dryland_session.json"))
    args = parser.parse_args()

    ctx = DrylandContext.model_validate_json(args.context.read_text())
    session = asyncio.run(run_agent(date.fromisoformat(args.date), ctx))
    args.output.write_text(session.model_dump_json(indent=2), encoding="utf-8")
    print(f"✅ Session saved to {args.output}")


if __name__ == "__main__":
    main()
"""
