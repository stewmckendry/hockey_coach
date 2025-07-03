# query_agent.py
from pathlib import Path
from pydantic import BaseModel
from agents import Agent

class ExpandedQuery(BaseModel):
    """Expanded query string for semantic search."""
    expanded_query: str

def _load_prompt() -> str:
    path = Path(__file__).resolve().parent.parent / "prompts" / "query_prompt.yaml"
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return "".join(lines[1:]).lstrip()

query_agent = Agent(
    name="QueryExpansionAgent",
    instructions=_load_prompt(),
    output_type=ExpandedQuery
)
