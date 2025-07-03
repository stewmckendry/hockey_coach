from __future__ import annotations
import json
from pydantic import BaseModel
from agents import Agent, Runner
from query_agent import ExpandedQuery, query_agent
from search_agent import SearchResults, search_agent
from summarizer_agent import summarizer_agent, SummaryInput, SummaryOutput
from reranker_agent import reranker_agent, RerankedResults

# === Prompt ===
DRILL_PLANNER_PROMPT = """
You are a hockey drill planning agent that orchestrates search and summarization.
You must:
- Expand the user's input into related terminology
- Retrieve relevant drills from the knowledge base
- Filter and re-rank them for quality
- If too few high-quality results are found, rerun search with feedback
- Summarize the best results
"""

# === Output Schema ===
class DrillPlannerOutput(BaseModel):
    expanded_query: ExpandedQuery
    results: SearchResults
    summary: SummaryOutput

# === Agent Wrapper ===
drill_planner_agent = Agent(
    name="DrillPlannerAgent",
    instructions=DRILL_PLANNER_PROMPT,
    handoffs=[query_agent, search_agent, reranker_agent, summarizer_agent],
    output_type=DrillPlannerOutput,
)

# === Manager ===
class DrillPlannerManager:
    def __init__(self, mcp_server=None, model=None) -> None:
        if model:
            for agent in [query_agent, search_agent, reranker_agent, summarizer_agent, drill_planner_agent]:
                agent.model = model
        if mcp_server:
            search_agent.mcp_servers = [mcp_server]
            drill_planner_agent.mcp_servers = [mcp_server]


    async def run(self, input_text: str, trace_id: str | None = None) -> DrillPlannerOutput:
        if trace_id:
            print(f"\n🔗 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")

        # Step 1: Expand query
        query_result = await Runner.run(query_agent, input_text)
        expanded = query_result.final_output_as(ExpandedQuery)

        # Step 2: Iterative search + rerank loop
        high_quality_drills = []
        feedback = ""
        max_iters = 5
        for i in range(max_iters):
            print(f"\n🔎 Search iteration {i+1}...")
            search_input = expanded.expanded_query + (" " + feedback if feedback else "")
            search_result = await Runner.run(search_agent, search_input)
            search_output = search_result.final_output_as(SearchResults)

            rerank_input = (
                f"User goal: {input_text}\n\n"
                f"Expanded query: {expanded.expanded_query}\n\n"
                f"Current drill candidates:\n{search_output.model_dump_json(indent=2)}\n\n"
                f"Top picks so far:\n{json.dumps(high_quality_drills, indent=2)}"
            )
            rerank_result = await Runner.run(reranker_agent, rerank_input)
            rerank_output = rerank_result.final_output_as(RerankedResults)

            # Create a lookup from title to full drill for enrichment
            drill_map = {d["title"]: d for d in search_output.drills}

            # Enrich high_quality_drills from titles to full DrillResult dicts
            enriched = [drill_map[title] for title in rerank_output.high_quality if title in drill_map]

            high_quality_drills.extend(enriched)
            feedback = rerank_output.feedback

            # Break if satisfied with results
            if len(high_quality_drills) >= 5 or not feedback:
                break

        # Step 3: Summarize
        summary_input = (
            f"User goal: {input_text}\n\n"
            f"Expanded query: {expanded.expanded_query}\n\n"
            f"Drills:\n{search_output.model_dump_json(indent=2)}"
        )
        summary_result = await Runner.run(summarizer_agent, summary_input)
        summary = summary_result.final_output_as(SummaryOutput)

        print(f"AI Coach Assistant: {summary.summary}\n")

        return DrillPlannerOutput(
            expanded_query=expanded,
            results=SearchResults(drills=high_quality_drills),
            summary=summary,
        )
