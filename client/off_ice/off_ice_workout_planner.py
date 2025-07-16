from __future__ import annotations

"""Orchestrator for off-ice workout plan generation."""

import base64
import binascii
import hashlib
import json
from pathlib import Path
from typing import Any, List, Optional

from pydantic import BaseModel
from agents import Agent, Runner, ImageGenerationTool
from agents.items import ImageGenerationCall, MessageOutputItem, ToolCallItem
from agents.mcp import MCPServerSse
from mcp_server.chroma_utils import get_chroma_collection

from .input_structurer import StructuredInput, input_structurer_agent
from .dryland_structure_agent import DrylandOutline, dryland_structure_agent
from .dryland_progression_agent import DrylandProgression, dryland_progression_agent
from .research_agent import ResearchSummary, research_agent
from .session_writer_agent import FinalPlan, PlanImage, session_writer_agent


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
        if model:
            research_agent.model = model
        if generate_images:
            session_writer_agent.tools = [
                ImageGenerationTool(
                    tool_config={"type": "image_generation", "quality": "low", "size": "1024x1024"}
                )
            ]

    async def run(self, input_text: str, trace_id: str | None = None) -> WorkoutPlanOutput:
        if trace_id:
            print(f"\n🔗 View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")

        # Step 1
        res = await Runner.run(input_structurer_agent, input_text)
        structured = res.final_output_as(StructuredInput)
        prev_id = res.last_response_id

        # Step 2
        res = await Runner.run(dryland_structure_agent, "", previous_response_id=prev_id)
        outline = res.final_output_as(DrylandOutline)
        prev_id = res.last_response_id
        self._write_json("dryland_structure.json", outline.model_dump())

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
        res = await Runner.run(session_writer_agent, "", previous_response_id=prev_id)
        final_plan = res.final_output_as(FinalPlan)

        self._write_draft(final_plan.final)

        captions: List[str] = []
        for item in res.new_items:
            if isinstance(item, MessageOutputItem):
                for block in item.raw_item.content:
                    if hasattr(block, "text"):
                        captions.append(block.text.strip())

        images: List[PlanImage] = []
        idx = 0
        for item in res.new_items:
            if isinstance(item, ToolCallItem) and isinstance(item.raw_item, ImageGenerationCall):
                b64_data = item.raw_item.result
                caption = captions[idx] if idx < len(captions) else ""
                idx += 1
                images.append(PlanImage(caption=caption, b64_json=b64_data))

        if images:
            final_plan.images = images

        file_path = self._save_markdown(final_plan, structured)
        self._index_plan(final_plan.final, structured, file_path)
        print(f"✅ Plan saved to {file_path}")
        return WorkoutPlanOutput(file_path=file_path, plan=final_plan.final)

    def _generated_base(self) -> Path:
        base = Path(__file__).resolve().parents[2] / "data" / "generated"
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
            indexed_dir = Path(__file__).resolve().parents[2] / "data" / "indexed" / "plans"
            indexed_dir.mkdir(parents=True, exist_ok=True)
            (indexed_dir / Path(file_path).name).write_text(text, encoding="utf-8")
        except Exception as e:
            print(f"❌ Failed to index plan into Chroma: {e}")
