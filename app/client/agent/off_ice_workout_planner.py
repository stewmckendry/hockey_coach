from __future__ import annotations

"""Multi-agent orchestration for generating an off-ice workout plan."""

from pathlib import Path
from typing import List
import hashlib
from pydantic import BaseModel

from agents import Agent, Runner
from agents.mcp import MCPServerSse
from .off_ice_planner import office_agent, OffIceSearchResults

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


# === Step 1: Input Structurer ===
class StructuredInput(BaseModel):
    age_group: str
    sport: str
    start_date: str
    end_date: str
    frequency: str
    goals: List[str]


input_structurer_agent = Agent(
    name="WorkoutInputStructurer",
    instructions=_load_prompt("off_ice_workout_input_prompt.yaml"),
    output_type=StructuredInput,
    mcp_servers=[MCPServerSse(name="Off-Ice KB MCP Server", params={"url": "http://localhost:8000/sse"})],
    model="gpt-4o",
)

# === Step 2: Plan Outliner ===
class PlanOutline(BaseModel):
    outline: str


plan_outliner_agent = Agent(
    name="WorkoutPlanOutliner",
    instructions=_load_prompt("off_ice_workout_outline_prompt.yaml"),
    output_type=PlanOutline,
    model="gpt-4o",
)

# === Step 3: Research Planner ===
class ResearchTopics(BaseModel):
    topics: List[str]


research_planner_agent = Agent(
    name="WorkoutResearchPlanner",
    instructions=_load_prompt("off_ice_workout_research_prompt.yaml"),
    output_type=ResearchTopics,
    model="gpt-4o",
)

# === Step 4: Web Researcher ===
class ResearchSummary(BaseModel):
    bullets: List[str]


from agents import WebSearchTool

web_researcher_agent = Agent(
    name="WorkoutWebResearcher",
    instructions=_load_prompt("off_ice_workout_web_prompt.yaml"),
    output_type=ResearchSummary,
    tools=[WebSearchTool()],
    model="gpt-4o",
)

# === Step 6: Synthesizer (after retrieval) ===
class DraftPlan(BaseModel):
    draft: str


synthesizer_agent = Agent(
    name="WorkoutSynthesizer",
    instructions=_load_prompt("off_ice_workout_synth_prompt.yaml"),
    output_type=DraftPlan,
    model="gpt-4o",
)

# === Step 7: Polisher ===
class FinalPlan(BaseModel):
    final: str


polisher_agent = Agent(
    name="WorkoutPolisher",
    instructions=_load_prompt("off_ice_workout_polish_prompt.yaml"),
    output_type=FinalPlan,
    model="gpt-4o",
)


class WorkoutPlanOutput(BaseModel):
    file_path: str
    plan: str


class OffIceWorkoutPlannerManager:
    def __init__(self, mcp_server=None, model=None) -> None:
        agents = [
            input_structurer_agent,
            plan_outliner_agent,
            research_planner_agent,
            web_researcher_agent,
            synthesizer_agent,
            polisher_agent,
            office_agent,
        ]
        if model:
            for a in agents:
                a.model = model
        if mcp_server:
            for a in agents:
                a.mcp_servers = [mcp_server]

    async def run(self, input_text: str, trace_id: str | None = None) -> WorkoutPlanOutput:
        if trace_id:
            print(f"\n🔗 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")

        # Step 1
        res = await Runner.run(input_structurer_agent, input_text)
        structured = res.final_output_as(StructuredInput)

        # Step 2
        res = await Runner.run(plan_outliner_agent, structured.model_dump_json(indent=2))
        outline = res.final_output_as(PlanOutline)

        # Step 3
        topics_input = (
            f"Input:\n{structured.model_dump_json(indent=2)}\n\nOutline:\n{outline.outline}"
        )
        res = await Runner.run(research_planner_agent, topics_input)
        topics = res.final_output_as(ResearchTopics)

        # Step 4
        res = await Runner.run(web_researcher_agent, "\n".join(topics.topics))
        research = res.final_output_as(ResearchSummary)

        # Step 5: Chroma retrieval using existing off-ice search agent
        search_query = "; ".join(structured.goals) + " " + outline.outline
        res = await Runner.run(office_agent, search_query)
        chroma_results = res.final_output_as(OffIceSearchResults)

        # Step 6
        synth_input = (
            f"STRUCTURED:\n{structured.model_dump_json(indent=2)}\n\n"
            f"OUTLINE:\n{outline.outline}\n\n"
            f"RESEARCH:\n{research.model_dump_json(indent=2)}\n\n"
            f"EXERCISES:\n{chroma_results.model_dump_json(indent=2)}"
        )
        res = await Runner.run(synthesizer_agent, synth_input)
        draft = res.final_output_as(DraftPlan)

        # Step 7
        res = await Runner.run(polisher_agent, draft.draft)
        final_plan = res.final_output_as(FinalPlan)

        # Step 8: Save markdown
        file_path = self._save_markdown(final_plan.final, structured)
        print(f"✅ Plan saved to {file_path}")

        return WorkoutPlanOutput(file_path=file_path, plan=final_plan.final)

    def _save_markdown(self, text: str, meta: StructuredInput) -> str:
        base = Path(__file__).resolve().parent.parent.parent.parent / "data" / "generated"
        base.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
        path = base / f"workout_plan_{digest}.md"
        frontmatter = (
            "---\n"
            f"title: Off-Ice Workout Plan\n"
            f"sport: {meta.sport}\n"
            f"age_group: {meta.age_group}\n"
            f"date_range: {meta.start_date} to {meta.end_date}\n"
            f"frequency: {meta.frequency}\n"
            f"goals: {'; '.join(meta.goals)}\n"
            "---\n\n"
        )
        path.write_text(frontmatter + text, encoding="utf-8")
        return str(path)
