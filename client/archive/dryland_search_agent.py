from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from pydantic import BaseModel
from agents import Agent, Runner
from agents.runner import RunState
from agents.items import MCPApprovalResponseItem
from agents.mcp import MCPServerSse

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts" / "off_ice"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


class DrylandSearchResults(BaseModel):
    drills: str


dryland_search_agent = Agent(
    name="DrylandSearchAgent",
    instructions=_load_prompt("off_ice_search_prompt.yaml"),
    output_type=DrylandSearchResults,
    mcp_servers=[
        MCPServerSse(
            name="Off-Ice KB MCP Server",
            params={"url": "http://localhost:8000/sse", "timeout": 30},
        )
    ],
    model="gpt-4o",
)



async def handle_elicitation(message, response_type, params, context):
    print(f"\n📝 MCP tool is asking: {message}")
    if response_type == str:
        user_input = input("Your input: ").strip()
        return {"action": "accept", "content": user_input}
    else:
        raise NotImplementedError("Only str elicitation is currently supported")


async def run_agent(text: str) -> tuple[DrylandSearchResults, str]:
    async with MCPServerSse(
        name="Off-Ice KB MCP Server",
        params={"url": "http://localhost:8000/sse", "timeout": 30},
        elicitation_handler=handle_elicitation  # add this here
    ) as session:

        res = await Runner.run(
            dryland_search_agent,
            text,
            session=session,
        )

        while res.interruptions:
            state = RunState(agent=dryland_search_agent, items=res.new_items)

            for interruption in res.interruptions:
                print(f"\n🛑 Agent wants to use tool: {interruption.raw_item.name}")
                print(f"With arguments: {interruption.raw_item.arguments}")
                decision = input("Approve this tool call? (y/n): ").strip().lower()
                if decision.startswith("y"):
                    comment = input("Optional comment for agent:\n> ")
                    state.approve(interruption, comment=comment)
                else:
                    state.reject(interruption)

            res = await Runner.run(dryland_search_agent, state, session=session)

    output = res.final_output_as(DrylandSearchResults)

    comment = ""
    for item in res.new_items:
        if isinstance(item, MCPApprovalResponseItem):
            try:
                comment = item.raw_item.comment  # type: ignore[attr-defined]
            except AttributeError:
                comment = getattr(item.raw_item, "input", "[Feedback not found]")

    return output, comment

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True, help="Practice planning request")
    args = parser.parse_args()

    drills, comment = asyncio.run(run_agent(args.text))

    print("\n✅ Final dryland drills:")
    print(drills.drills)

    if comment:
        print(f"\n💬 Final coach comment: {comment}")


if __name__ == "__main__":
    main()
