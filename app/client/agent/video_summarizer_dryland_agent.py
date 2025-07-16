from pathlib import Path
from pydantic import BaseModel
from agents import Agent

class VideoSummaryDrylandOutput(BaseModel):
    summary: str
    teaching_points: list[str]
    visual_prompt: str
    training_focus: list[str]
    position: list[str] | None = []
    complexity: str | None = None
    clip_type: str | None = None
    intended_audience: str | None = None
    play_or_skill_focus: str | None = None


def _load_prompt() -> str:
    path = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "prompts"
        / "video_summarizer_prompt_dryland.yaml"
    )
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()

video_summarizer_dryland_agent = Agent(
    name="VideoSummarizerDrylandAgent",
    instructions=_load_prompt(),
    output_type=VideoSummaryDrylandOutput,
)
