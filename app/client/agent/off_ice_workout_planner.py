from __future__ import annotations

"""Multi-agent orchestration for generating an off-ice workout plan."""

from pathlib import Path
from typing import List, Optional, Any
import hashlib
import json
from datetime import datetime
import base64
import binascii

from pydantic import BaseModel
from agents import Agent, Runner, ImageGenerationTool, function_tool
from agents.items import ToolCallItem, ImageGenerationCall, MessageOutputItem
from agents.mcp import MCPServerSse
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


# === Step 2: Dryland Session Structure ===
class DrylandStructure(BaseModel):
    agenda: str


dryland_structure_agent = Agent(
    name="DrylandStructureAgent",
    instructions=_load_prompt("off_ice_workout_outline_prompt.yaml"),
    output_type=DrylandStructure,
    mcp_servers=[MCPServerSse(name="Off-Ice KB MCP Server", params={"url": "http://localhost:8000/sse", "timeout": 30})],
    model="gpt-4o",
)


# === Step 3: Progression Planner ===
class DrylandProgression(BaseModel):
    progression: str


dryland_progression_agent = Agent(
    name="DrylandProgressionAgent",
    instructions=_load_prompt("off_ice_workout_progression_prompt.yaml"),
    output_type=DrylandProgression,
    mcp_servers=[MCPServerSse(name="Off-Ice KB MCP Server", params={"url": "http://localhost:8000/sse", "timeout": 30})],
    model="gpt-4o",
)


# === Step 4: Research Agent ===
class ResearchSummary(BaseModel):
    bullets: List[str]


from agents import WebSearchTool

research_agent = Agent(
    name="WorkoutResearcher",
    instructions=_load_prompt("off_ice_workout_web_prompt.yaml"),
    output_type=ResearchSummary,
    tools=[WebSearchTool()],
    model="gpt-4o",
)


# === Step 5: Writer ===
class PlanImage(BaseModel):
    caption: Optional[str]
    b64_json: Optional[str]


class FinalPlan(BaseModel):
    final: str
    images: Optional[List[PlanImage]] = None


class WorkoutPlanOutput(BaseModel):
    file_path: str
    plan: str


def fix_base64_padding(b64: str) -> str:
    return b64 + "=" * (-len(b64) % 4)


class OffIceWorkoutPlannerManager:
    def __init__(self, mcp_server: MCPServerSse | None = None, model: str | None = None, generate_images: bool = False) -> None:
        for agent in [dryland_structure_agent, dryland_progression_agent]:
            if mcp_server:
                agent.mcp_servers = [mcp_server]
            if model:
                agent.model = model

        # if mcp_server:
        #     research_agent.mcp_servers = [mcp_server]
        if model:
            research_agent.model = model

        tools: List[Any] = []
        if generate_images:
            tools.append(
                ImageGenerationTool(
                    tool_config={"type": "image_generation", "quality": "low", "size": "1024x1024"}
                )
            )

        self.writer_agent = Agent(
            name="WorkoutWriter",
            instructions=_load_prompt("off_ice_workout_synth_prompt.yaml"),
            output_type=FinalPlan,
            tools=tools,
            model=model or "gpt-4o",
        )

    async def run(self, input_text: str, trace_id: str | None = None) -> WorkoutPlanOutput:
        if trace_id:
            print(f"\n🔗 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")

        # Step 1
        res = await Runner.run(input_structurer_agent, input_text)
        structured = res.final_output_as(StructuredInput)
        prev_id = res.last_response_id

        # Step 2
        res = await Runner.run(dryland_structure_agent, "", previous_response_id=prev_id)
        structure = res.final_output_as(DrylandStructure)
        prev_id = res.last_response_id
        self._write_json("dryland_structure.json", structure.model_dump())

        # Step 3
        res = await Runner.run(dryland_progression_agent, "", previous_response_id=prev_id)
        progression = res.final_output_as(DrylandProgression)
        prev_id = res.last_response_id
        self._write_json("dryland_progression.json", progression.model_dump())

        # Step 4
        res = await Runner.run(research_agent, "", max_turns=10, previous_response_id=prev_id)
        research = res.final_output_as(ResearchSummary)
        prev_id = res.last_response_id

        # Step 5
        res = await Runner.run(self.writer_agent, "", previous_response_id=prev_id)
        final_plan = res.final_output_as(FinalPlan)

        # Save draft
        self._write_draft(final_plan.final)

        captions: List[str] = []
        for item in res.new_items:
            if isinstance(item, MessageOutputItem):
                for block in item.raw_item.content:
                    if hasattr(block, "text"):
                        captions.append(block.text.strip())

        generated_images: List[PlanImage] = []
        image_index = 0
        for item in res.new_items:
            if isinstance(item, ToolCallItem) and isinstance(item.raw_item, ImageGenerationCall):
                b64_data = item.raw_item.result
                caption = captions[image_index] if image_index < len(captions) else ""
                image_index += 1
                generated_images.append(PlanImage(caption=caption, b64_json=b64_data))

        if generated_images:
            final_plan.images = generated_images

        file_path = self._save_markdown(final_plan, structured)
        self._index_plan(final_plan.final, structured, file_path)
        print(f"✅ Plan saved to {file_path}")
        return WorkoutPlanOutput(file_path=file_path, plan=final_plan.final)

    def _generated_base(self) -> Path:
        base = Path(__file__).resolve().parent.parent.parent.parent / "data" / "generated"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def _write_json(self, filename: str, data: Any) -> None:
        path = self._generated_base() / filename
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _write_draft(self, text: str) -> None:
        path = self._generated_base() / "draft_plan.md"
        path.write_text(text, encoding="utf-8")

    def _save_markdown(self, plan: FinalPlan, meta: StructuredInput) -> str:
        base = self._generated_base()
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
                if not img.b64_json:
                    continue
                try:
                    img_data = base64.b64decode(fix_base64_padding(img.b64_json))
                except (binascii.Error, ValueError) as e:
                    print(f"⚠️ Skipping image {i} due to decode error: {e}")
                    continue
                img_filename = f"{digest}_{i}.png"
                img_path = images_dir / img_filename
                with open(img_path, "wb") as f:
                    f.write(img_data)
                caption = img.caption or ""
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
            indexed_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "indexed" / "plans"
            indexed_dir.mkdir(parents=True, exist_ok=True)
            (indexed_dir / Path(file_path).name).write_text(text, encoding="utf-8")
        except Exception as e:
            print(f"❌ Failed to index plan into Chroma: {e}")

