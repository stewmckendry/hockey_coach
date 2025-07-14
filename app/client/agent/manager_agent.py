from __future__ import annotations

"""Manager agent demonstrating an elicitation flow."""

from uuid import uuid4
from pydantic import BaseModel
from agents import Agent, Runner
from agents.mcp import MCPServerSse


class ManagerOutput(BaseModel):
    plan: str


def _instructions() -> str:
    return (
        "You plan a short hockey practice. "
        "If no skill focus is provided, call `mcp_elicitation_tool` with the given session_id. "
        "Once a skill is returned, acknowledge it in your plan."
    )


manager_agent = Agent(
    name="PracticeManager",
    instructions=_instructions(),
    output_type=ManagerOutput,
    mcp_servers=[MCPServerSse(name="ToolServer", params={"url": "http://localhost:8000/sse"})],
    model="gpt-4o",
)


class ManagerRunner:
    def __init__(self, server: MCPServerSse | None = None) -> None:
        if server:
            manager_agent.mcp_servers = [server]

    async def run(self, goal: str, skill: str | None = None, session_id: str | None = None) -> ManagerOutput:
        session_id = session_id or str(uuid4())
        input_text = (
            f"Goal: {goal}\n"
            f"Skill focus: {skill or ''}\n"
            f"Session: {session_id}"
        )
        result = await Runner.run(manager_agent, input_text)
        return result.final_output_as(ManagerOutput)
