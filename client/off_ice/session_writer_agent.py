from __future__ import annotations

"""Agent to synthesize the final off-ice workout plan."""

import argparse
import asyncio
import base64
import binascii
import json
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel
from agents import Agent, Runner, ImageGenerationTool
from agents.items import ImageGenerationCall, MessageOutputItem, ToolCallItem

from .input_structurer import StructuredInput
from .dryland_structure_agent import DrylandOutline
from .dryland_progression_agent import DrylandProgression
from .research_agent import ResearchSummary
from .dryland_video_summary_agent import VideoSummary

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts" / "off_ice"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()


class PlanImage(BaseModel):
    caption: Optional[str]
    b64_json: Optional[str]


class FinalPlan(BaseModel):
    final: str
    images: Optional[List[PlanImage]] = None


session_writer_agent = Agent(
    name="WorkoutWriter",
    instructions=_load_prompt("synth_prompt.yaml"),
    output_type=FinalPlan,
    model="gpt-4o",
)


async def run_agent(
    structured: StructuredInput,
    outline: DrylandOutline,
    progression: DrylandProgression,
    research: ResearchSummary,
    video_summary: VideoSummary | None = None,
    generate_images: bool = False,
) -> FinalPlan:
    tools: List[ImageGenerationTool] = []
    if generate_images:
        tools.append(
            ImageGenerationTool(
                tool_config={"type": "image_generation", "quality": "low", "size": "1024x1024"}
            )
        )
    session_writer_agent.tools = tools

    context = {
        "structured": structured.model_dump(),
        "outline": outline.model_dump(),
        "progression": progression.model_dump(),
        "research": research.model_dump(),
    }
    if video_summary:
        context["video_summary"] = (
            video_summary.model_dump() if isinstance(video_summary, BaseModel) else video_summary
        )
    res = await Runner.run(session_writer_agent, json.dumps(context))
    final_plan = res.final_output_as(FinalPlan)

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
            data = item.raw_item.result
            caption = captions[idx] if idx < len(captions) else ""
            idx += 1
            images.append(PlanImage(caption=caption, b64_json=data))

    if images:
        final_plan.images = images
    return final_plan


def fix_base64_padding(b64: str) -> str:
    return b64 + "=" * (-len(b64) % 4)


def save_plan(plan: FinalPlan, output: Path) -> None:
    output.write_text(plan.final, encoding="utf-8")
    images_dir = output.parent / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    stem = output.stem
    if plan.images:
        for i, img in enumerate(plan.images):
            if not img.b64_json:
                continue
            try:
                img_data = base64.b64decode(fix_base64_padding(img.b64_json))
            except (binascii.Error, ValueError):
                continue
            img_path = images_dir / f"{stem}_{i}.png"
            with open(img_path, "wb") as f:
                f.write(img_data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structured", type=Path, required=True)
    parser.add_argument("--outline", type=Path, required=True)
    parser.add_argument("--progression", type=Path, required=True)
    parser.add_argument("--research", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("workout_plan.md"))
    parser.add_argument("--generate-images", action="store_true")
    parser.add_argument("--video-summary", type=Path, help="Optional video summary markdown")
    args = parser.parse_args()

    structured = StructuredInput.model_validate_json(args.structured.read_text())
    outline = DrylandOutline.model_validate_json(args.outline.read_text())
    progression = DrylandProgression.model_validate_json(args.progression.read_text())
    research = ResearchSummary.model_validate_json(args.research.read_text())

    video_summary = None
    if args.video_summary and args.video_summary.exists():
        video_summary = VideoSummary(markdown=args.video_summary.read_text())

    plan = asyncio.run(
        run_agent(structured, outline, progression, research, video_summary=video_summary, generate_images=args.generate_images)
    )
    save_plan(plan, args.output)
    print(f"✅ Final plan saved to {args.output}")


if __name__ == "__main__":
    main()
