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
from .dryland_planner_agent import dryland_planner_agent
from .dryland_session_agent import dryland_session_agent

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


chat_agent = Agent[PracticePlanningContext](
    name="DrylandDrillPlanner",
    instructions=_load_prompt("off_ice_search_prompt.yaml"),
    model="gpt-4o",
    output_type=None,
    tools=[set_practice_context_param],
    mcp_servers=[
        MCPServerSse(
            name="Off-Ice KB MCP Server",
            params={"url": "http://localhost:8000/sse", "timeout": 30},
        )
    ],
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
    end_on_output: bool = False,
) -> Any:
    input_items: list[TResponseInputItem] = []
    if initial_input:
        input_items.append({"role": "user", "content": initial_input})

    while True:
        result = await Runner.run(agent, input_items or "", context=context)
        _print_items(result.new_items)
        input_items = result.to_input_list()
        if end_on_output and result.final_output:
            print(f"\n✅ Final output:\n{result.final_output}\n")
            return result.final_output
        user = input("\n👤 Coach: ").strip()
        if user.lower() in {"exit", "quit"}:
            print("👋 Exiting.")
            return result.final_output
        input_items.append({"role": "user", "content": user})


async def run_pipeline() -> None:
    mode = input("Plan, Session, or Chat? ").strip().lower()
    if mode.startswith("p"):
        ctx = DrylandContext()
        await run_loop(dryland_planner_agent, ctx, initial_input="", end_on_output=True)
    elif mode.startswith("s"):
        date_str = input("Which date? (YYYY-MM-DD): ").strip()
        try:
            ses_date = date.fromisoformat(date_str)
        except ValueError:
            print("Invalid date. Using today.")
            ses_date = date.today()
        ctx = DrylandContext()
        await run_loop(
            dryland_session_agent,
            ctx,
            initial_input=ses_date.isoformat(),
            end_on_output=True,
        )
    else:
        ctx = PracticePlanningContext()
        await run_loop(chat_agent, ctx)


def main() -> None:
    if not shutil.which("uv"):
        raise RuntimeError("Missing `uv`. Install it from https://docs.astral.sh/uv/")
    print("🚀 Launching Thunder MCP SSE server at http://localhost:8000/sse ...")
    server_path = (
        Path(__file__).resolve().parents[1]
        / "mcp_server"
        / "off_ice"
        / "off_ice_mcp_server.py"
    )
    process: subprocess.Popen[Any] | None = subprocess.Popen(
        ["uv", "run", str(server_path)]
    )
    time.sleep(3)
    print("✅ Server started. Connecting agent...\n")
    try:
        asyncio.run(run_pipeline())
    finally:
        if process:
            print("\n🛑 Shutting down server...")
            process.terminate()


if __name__ == "__main__":
    main()
