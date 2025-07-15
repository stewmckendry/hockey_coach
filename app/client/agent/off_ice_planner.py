from __future__ import annotations

from typing import List, Optional
from pathlib import Path

from pydantic import BaseModel
from agents import Agent, Runner
from agents.mcp import MCPServerSse


OFFICE_SEARCH_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "prompts"
    / "off_ice_search_prompt.yaml"
)


def _load_prompt() -> str:
    with open(OFFICE_SEARCH_PROMPT_PATH, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


class OffIceSearchResult(BaseModel):
    title: str
    category: str
    focus_area: str
    teaching_complexity: str
    progression_stage: str
    description: str
    equipment_needed: Optional[str] = None
    source_pages: str


class OffIceSearchResults(BaseModel):
    items: List[OffIceSearchResult]


office_agent = Agent(
    name="OffIceSearchAgent",
    instructions=_load_prompt(),
    handoffs=[],
    output_type=OffIceSearchResults,
    mcp_servers=[MCPServerSse(name="Thunder MCP Server", params={"url": "http://localhost:8000/sse"})],
    model="gpt-4o",
)


class OffIcePlannerManager:
    def __init__(self, mcp_server=None, model=None) -> None:
        if model:
            office_agent.model = model
        if mcp_server:
            office_agent.mcp_servers = [mcp_server]

    async def run(self, input_text: str, trace_id: str | None = None) -> OffIceSearchResults:
        if trace_id:
            print(f"\n🔗 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")

        result = await Runner.run(office_agent, input_text)
        output = result.final_output_as(OffIceSearchResults)

        # Safeguards: limit results and validate required fields
        output.items = output.items[:10]
        for item in output.items:
            if not (item.title and item.description and item.category and item.focus_area):
                raise ValueError("Incomplete off-ice search result")
        return output

