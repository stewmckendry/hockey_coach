from __future__ import annotations

from client.shared.agent_templates import create_research_agent
from client.off_ice.dryland_context import DrylandContext
from client.off_ice.dryland_context_tools import set_dryland_context_param
from agents.tools import WebSearchTool
from utils.prompts import load_prompt_yaml


def get_dryland_research_agent(mcp_server):
    prompt = load_prompt_yaml("prompts/off_ice/dryland_research_prompt.yaml")
    return create_research_agent(
        context_class=DrylandContext,
        prompt=prompt,
        tools=[WebSearchTool(), set_dryland_context_param],
        name="DrylandResearchAgent",
        mcp_servers=[mcp_server],
    )
