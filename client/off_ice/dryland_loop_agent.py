from __future__ import annotations

import asyncio
import shutil
import subprocess
import time
from datetime import date
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from agents import (
    Agent,
    Runner,
    ItemHelpers,
    function_tool,
    ToolCallItem,
    ToolCallOutputItem,
    MessageOutputItem,
    HandoffOutputItem,
    RunContextWrapper,
)
from agents.items import TResponseInputItem
from agents.mcp import MCPServerSse

from models.dryland_models import DrylandContext
from dryland_planner_agent import get_dryland_planner_agent
from dryland_session_agent import get_dryland_session_agent

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts" / "off_ice"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


class PracticePlanningContext(BaseModel):
    age_group: str | None = None
    focus_area: str | None = None
    equipment: list[str] = []
    coach_notes: str | None = None
    preferred_complexity: str | None = None


@function_tool
async def set_practice_context_param(
    ctx: RunContextWrapper[PracticePlanningContext],
    key: Literal["age_group", "focus_area", "preferred_complexity", "coach_notes"],
    value: str,
) -> str:
    setattr(ctx.context, key, value)
    return f"Set {key} to {value}"

mcp_server = MCPServerSse(
    name="Off-Ice KB MCP Server",
    params={"url": "http://localhost:8000/sse", "timeout": 30},
)

chat_agent = Agent[PracticePlanningContext](
    name="DrylandDrillPlanner",
    instructions=_load_prompt("off_ice_search_prompt.yaml"),
    model="gpt-4o",
    output_type=None,
    tools=[set_practice_context_param],
    mcp_servers=[mcp_server],
)


def _print_items(items: list[Any]) -> None:
    for item in items:
        name = item.agent.name
        if isinstance(item, MessageOutputItem):
            print(f"{name}: {ItemHelpers.text_message_output(item)}")
        elif isinstance(item, ToolCallItem):
            print(f"{name} → Calling tool: {item.raw_item.name}")
        elif isinstance(item, ToolCallOutputItem):
            print(f"{name} → Tool result: {item.output}")
        elif isinstance(item, HandoffOutputItem):
            print(f"🔁 Handoff: {item.source_agent.name} → {item.target_agent.name}")
        else:
            print(f"{name}: (Unhandled item: {item.__class__.__name__})")


async def run_loop(
    agent: Agent[Any],
    context: Any,
    *,
    initial_input: str = "",
) -> Any:
    input_items: list[TResponseInputItem] = []
    if initial_input:
        input_items.append({"role": "user", "content": initial_input})

    while True:
        result = await Runner.run(agent, input_items or "", context=context)
        for item in result.new_items:
            name = item.agent.name
            if isinstance(item, MessageOutputItem):
                print(f"{name}: {ItemHelpers.text_message_output(item)}")
            elif isinstance(item, ToolCallItem):
                print(f"{name} → Calling tool: {item.raw_item.name}")
            elif isinstance(item, ToolCallOutputItem):
                print(f"{name} → Tool result: {item.output}")
            elif isinstance(item, HandoffOutputItem):
                print(f"🔁 Handoff: {item.source_agent.name} → {item.target_agent.name}")
            else:
                print(f"{name}: (Unhandled item: {item.__class__.__name__})")
        input_items = result.to_input_list()
        user = input("\n👤 Coach: ").strip()
        if user.lower() in {"exit", "quit"}:
            print("\n📋 Final plan context:")
            print(context.plan.model_dump_json(indent=2) if context.plan else "(No plan saved)")
            print("👋 Exiting.")
            return result.final_output
        input_items.append({"role": "user", "content": user})


async def run_pipeline() -> None:
    mode = input("Plan, Session, or Chat? ").strip().lower()
    if mode.startswith("p"):
        print("🏒 Dryland Planner")
        ctx = DrylandContext()
        planner_agent = get_dryland_planner_agent(mcp_server)
        await run_loop(planner_agent, ctx)
    elif mode.startswith("s"):
        print("🏒 Dryland Session")
        date_str = input("Which date? (YYYY-MM-DD): ").strip()
        try:
            ses_date = date.fromisoformat(date_str)
        except ValueError:
            print("Invalid date. Using today.")
            ses_date = date.today()
        ctx = DrylandContext()
        session_agent = get_dryland_session_agent(mcp_server)
        await run_loop(
            session_agent,
            ctx,
            initial_input=ses_date.isoformat()
        )
    else:
        ctx = PracticePlanningContext()
        await run_loop(chat_agent, ctx)


async def main() -> None:
    print("🏒 Dryland Drill Planning Assistant — Multi-Turn Mode")
    async with mcp_server:
        await run_pipeline()

if __name__ == "__main__":
    asyncio.run(main())

