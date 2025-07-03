# search_agent.py
from pathlib import Path
from typing import List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel
from agents import Agent
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings

# === Output model ===
class DrillResult(TypedDict):
    title: str
    link: Optional[str]
    hockey_skills: List[str]
    position: List[str]
    situation: List[str]
    source: str

class SearchResults(BaseModel):
    """Results returned from drill search."""
    drills: List[DrillResult]

# === Load Prompt ===
def _load_prompt() -> str:
    path = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "search_prompt.yaml"
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return "".join(lines[1:]).lstrip()

# === Define Search Agent ===
search_agent = Agent(
    name="SearchAgent",
    instructions=_load_prompt(),
    output_type=SearchResults,
    mcp_servers=[MCPServerSse(name="Thunder MCP Server", params={"url": "http://localhost:8000/sse"})],
    model="gpt-4o",
    model_settings=ModelSettings(tool_choice="required"),
)
