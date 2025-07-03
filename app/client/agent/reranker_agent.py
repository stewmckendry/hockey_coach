from typing import List
from agents import Agent
from pydantic import BaseModel
from pathlib import Path

# --- Output ---
class DrillRating(BaseModel):
    title: str
    relevance_score: float  # 0.0 to 1.0
    reason: str

class RerankedResults(BaseModel):
    reranked: List[DrillRating]
    high_quality: List[str]  # titles of drills with score > threshold
    feedback: str  # Guidance to improve future searches

# --- Prompt Loader ---
def _load_prompt() -> str:
    path = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "rerank_prompt.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return "".join(f.readlines()[1:]).lstrip()

# --- Agent ---
reranker_agent = Agent(
    name="RerankerAgent",
    instructions=_load_prompt(),
    output_type=RerankedResults,
)
