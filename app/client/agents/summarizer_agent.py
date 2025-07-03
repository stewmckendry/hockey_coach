# summarizer_agent.py
from pathlib import Path
from pydantic import BaseModel
from agents import Agent

class SummaryInput(BaseModel):
    user_goal: str
    expanded_query: str
    drills_json: str

class SummaryOutput(BaseModel):
    summary: str

def _load_prompt() -> str:
    path = Path(__file__).resolve().parent.parent / "prompts" / "summarizer_prompt.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()

summarizer_agent = Agent(
    name="DrillSummarizerAgent",
    instructions=_load_prompt(),
    output_type=SummaryOutput
)
