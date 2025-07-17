from __future__ import annotations
import asyncio
from pathlib import Path
from pydantic import BaseModel
from typing import Literal

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

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts" / "off_ice"

def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


# 🧠 Shared persistent memory
class PracticePlanningContext(BaseModel):
    age_group: str | None = None
    focus_area: str | None = None
    equipment: list[str] = []
    coach_notes: str | None = None
    preferred_complexity: str | None = None


# ✅ New tool to update context
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

dryland_agent = Agent[PracticePlanningContext](
    name="DrylandDrillPlanner",
    instructions=_load_prompt("off_ice_search_prompt.yaml"),
    model="gpt-4o",
    output_type=None,
    tools=[set_practice_context_param],  # 👈 registered tool
    mcp_servers=[mcp_server],
)

async def main():
    await mcp_server.connect()
    context = PracticePlanningContext()
    input_items: list[TResponseInputItem] = []
    print("🏒 Dryland Drill Planning Assistant — Multi-Turn Mode")

    async with MCPServerSse(
        name="Off-Ice KB MCP Server",
        params={"url": "http://localhost:8000/sse", "timeout": 30},
    ) as session:
        while True:
            user_input = input("\n👤 Coach: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Exiting.")
                break

            input_items.append({"role": "user", "content": user_input})
            result = await Runner.run(dryland_agent, input_items, context=context)

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

if __name__ == "__main__":
    asyncio.run(main())
