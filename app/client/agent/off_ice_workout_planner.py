from __future__ import annotations

"""Multi-agent orchestration for generating an off-ice workout plan."""

from pathlib import Path
from typing import List, Optional
import hashlib
from datetime import datetime, timedelta
import dateparser
from pydantic import BaseModel
import base64

from agents import Agent, Runner, ImageGenerationTool, function_tool
from .off_ice_planner import office_agent, OffIceSearchResults
from app.mcp_server.chroma_utils import get_chroma_collection

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
    location: str
    amenities: List[str]
    preferred_activities: List[str]

@function_tool
def get_current_date() -> str:
    """Return today's date in ISO format."""
    return datetime.now().date().isoformat()


input_structurer_agent = Agent(
    name="WorkoutInputStructurer",
    instructions=_load_prompt("off_ice_workout_input_prompt.yaml"),
    output_type=StructuredInput,
    tools=[get_current_date],
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
class PlanImage(BaseModel):
    caption: Optional[str]
    b64_json: Optional[str]

class FinalPlan(BaseModel):
    final: str
    images: Optional[List[PlanImage]] = None


polisher_agent = Agent(
    name="WorkoutPolisher",
    instructions=_load_prompt("off_ice_workout_polish_prompt.yaml"),
    output_type=FinalPlan,
    model="gpt-4o",
    tools=[
        ImageGenerationTool(
            tool_config={
                "type": "image_generation"
            }
        )
    ]
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
        office_agent.mcp_servers = [mcp_server] if mcp_server else office_agent.mcp_servers

    async def run(
        self, input_text: str, trace_id: str | None = None
    ) -> WorkoutPlanOutput:
        if trace_id:
            print(
                f"\n🔗 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n"
            )

        # Step 1
        res = await Runner.run(input_structurer_agent, input_text)
        structured = res.final_output_as(StructuredInput)
        prev_id = res.last_response_id

        # Step 2
        res = await Runner.run(
            plan_outliner_agent,
            "",
            previous_response_id=prev_id,
        )
        outline = res.final_output_as(PlanOutline)
        prev_id = res.last_response_id

        # Step 3
        res = await Runner.run(
            research_planner_agent,
            "",
            previous_response_id=prev_id,
        )
        topics = res.final_output_as(ResearchTopics)
        prev_id = res.last_response_id

        # Step 4
        res = await Runner.run(
            web_researcher_agent,
            "",
            max_turns=10,
            previous_response_id=prev_id,
        )
        research = res.final_output_as(ResearchSummary)
        prev_id = res.last_response_id

        # Step 5: Chroma retrieval using existing off-ice search agent
        res = await Runner.run(
            office_agent,
            "",
            previous_response_id=prev_id,
        )
        chroma_results = res.final_output_as(OffIceSearchResults)
        prev_id = res.last_response_id

        # Step 6
        res = await Runner.run(
            synthesizer_agent,
            "",
            previous_response_id=prev_id,
        )
        draft = res.final_output_as(DraftPlan)
        prev_id = res.last_response_id

        # Step 7
        res = await Runner.run(
            polisher_agent,
            "",
            previous_response_id=prev_id,
        )
        final_plan = res.final_output_as(FinalPlan)
        prev_id = res.last_response_id

        # Step 8: Save markdown
        file_path = self._save_markdown(final_plan, structured)
        self._index_plan(final_plan.final, structured, file_path)
        print(f"✅ Plan saved to {file_path}")

        return WorkoutPlanOutput(file_path=file_path, plan=final_plan.final)

    def _save_markdown(self, plan: FinalPlan, meta: StructuredInput) -> str:
        base = (
            Path(__file__).resolve().parent.parent.parent.parent / "data" / "generated"
        )
        base.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha1(plan.final.encode("utf-8")).hexdigest()[:8]
        images_dir = base / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        path = base / f"workout_plan_{digest}.md"
        frontmatter = (
            "---\n"
            f"title: Off-Ice Workout Plan\n"
            f"sport: {meta.sport}\n"
            f"age_group: {meta.age_group}\n"
            f"date_range: {meta.start_date} to {meta.end_date}\n"
            f"frequency: {meta.frequency}\n"
            f"goals: {'; '.join(meta.goals)}\n"
            f"location: {meta.location}\n"
            f"amenities: {'; '.join(meta.amenities)}\n"
            f"preferred_activities: {'; '.join(meta.preferred_activities)}\n"
            "---\n\n"
        )
        body = "# Off-Ice Workout Overview\n\n" + plan.final

        visuals_md = ""
        if plan.images:
            visuals_md += "\n\n### Visuals\n\n"
            for i, img in enumerate(plan.images):
                img_data = base64.b64decode(img.get("b64_json", ""))
                img_filename = f"{digest}_{i}.png"
                img_path = images_dir / img_filename
                with open(img_path, "wb") as f:
                    f.write(img_data)
                caption = img.get("caption", "")
                # Optional caption file
                (images_dir / f"{digest}_{i}_caption.txt").write_text(caption, encoding="utf-8")
                visuals_md += f"![{caption}](images/{img_filename})\n"

        path.write_text(frontmatter + body + visuals_md, encoding="utf-8")
        return str(path)

    def _index_plan(self, text: str, meta: StructuredInput, file_path: str) -> None:
        collection = get_chroma_collection()
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
        doc_id = f"plan-{digest}"
        metadata = {
            "age_group": meta.age_group,
            "sport": meta.sport,
            "start_date": meta.start_date,
            "end_date": meta.end_date,
            "goals": "; ".join(meta.goals),
            "location": meta.location,
            "amenities": "; ".join(meta.amenities),
            "preferred_activities": "; ".join(meta.preferred_activities),
            "file_path": file_path,
            "type": "off_ice_plan",
        }
        try:
            collection.add(documents=[text], metadatas=[metadata], ids=[doc_id])
            indexed_dir = (
                Path(__file__).resolve().parent.parent.parent.parent
                / "data"
                / "indexed"
                / "plans"
            )
            indexed_dir.mkdir(parents=True, exist_ok=True)
            (indexed_dir / Path(file_path).name).write_text(text, encoding="utf-8")
        except Exception as e:
            print(f"❌ Failed to index plan into Chroma: {e}")
