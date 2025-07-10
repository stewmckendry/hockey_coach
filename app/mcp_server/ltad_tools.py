"""MCP tools for querying LTAD skill knowledge."""

from __future__ import annotations
import json
from pathlib import Path
from typing import List, TypedDict

from mcp.server.fastmcp import FastMCP

from .chroma_utils import get_client, _embed

mcp = FastMCP("Thunder LTAD")

LTAD_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "ltad_skills_final.json"


class LTADSkill(TypedDict):
    age_groups: List[str]
    ltad_stage: str | None
    position: List[str]
    skill_category: str
    skill_name: str
    teaching_notes: str
    season_month: str | None
    source: str


def _load_data() -> List[LTADSkill]:
    if not LTAD_PATH.exists():
        return []
    with open(LTAD_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool("get_skills_by_age")
def get_skills_by_age(age_group: str) -> List[LTADSkill]:
    """Return LTAD skills for a specific age group."""
    data = _load_data()
    return [s for s in data if age_group in s.get("age_groups", [])]


@mcp.tool("get_skills_by_position")
def get_skills_by_position(position: str) -> List[LTADSkill]:
    """Return LTAD skills for a given position."""
    pos = position.lower()
    data = _load_data()
    return [s for s in data if any(pos == p.lower() for p in s.get("position", []))]


client = get_client()
ltad_collection = client.get_or_create_collection("ltad_index", embedding_function=_embed)


@mcp.tool("search_ltad_knowledge")
def search_ltad_knowledge(query: str, n_results: int = 5) -> List[LTADSkill]:
    """Semantic search over the LTAD knowledge base."""
    results = ltad_collection.query(query_texts=[query], n_results=n_results)
    return results.get("metadatas", [[]])[0]
