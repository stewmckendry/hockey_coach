# manager.py
from __future__ import annotations
from pydantic import BaseModel
from agents import Agent, Runner
from agents.extensions.visualization import draw_graph

from query_agent import ExpandedQuery, query_agent
from search_agent import SearchResults, search_agent
from summarizer_agent import summarizer_agent, SummaryInput, SummaryOutput

DRILL_PLANNER_PROMPT = (
    "You are a drill planner that helps coaches find relevant hockey drills.\n"
    "You first expand the user query with terminology, then search the drill KB.\n"
    "Use your sub-agents to improve accuracy and relevance."
)

class DrillPlannerOutput(BaseModel):
    """Final output of the drill planner."""
    expanded_query: ExpandedQuery
    results: SearchResults
    summary: SummaryOutput

drill_planner_agent = Agent(
    name="DrillPlannerAgent",
    instructions=DRILL_PLANNER_PROMPT,
    handoffs=[query_agent, search_agent, summarizer_agent],
    output_type=DrillPlannerOutput,
)

class DrillPlannerManager:
    """Orchestrates the drill planning agents."""

    def __init__(self, mcp_server=None, model=None):
        if model:
            for agent in [query_agent, search_agent, drill_planner_agent]:
                agent.model = model
        if mcp_server:
            search_agent.mcp_servers = [mcp_server]
            drill_planner_agent.mcp_servers = [mcp_server]

    async def run(self, input_text: str, trace_id: str | None = None) -> DrillPlannerOutput:
        if trace_id:
            print(f"🔗 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")

        query_result = await Runner.run(query_agent, input_text)
        expanded = query_result.final_output_as(ExpandedQuery)

        search_result = await Runner.run(search_agent, expanded.expanded_query)
        results = search_result.final_output_as(SearchResults)

        # 👉 Summarize
        summary_input = (
            f"User goal: {input_text}\n\n"
            f"Expanded query: {expanded.expanded_query}\n\n"
            f"Drills:\n{results.model_dump_json(indent=2)}"
        )
        summary_result = await Runner.run(summarizer_agent, summary_input)
        friendly_response = summary_result.final_output_as(SummaryOutput)

        print("\n🧠 Assistant:", friendly_response.summary)

        return DrillPlannerOutput(
            expanded_query=expanded,
            results=results,
            summary=friendly_response
        )


def visualize_workflow(filename: str | None = None):
    """Visualize the agent workflow."""
    return draw_graph(drill_planner_agent, filename=filename)
