from __future__ import annotations

"""MCP server exposing off-ice training search tools."""

from typing import List, Optional, TypedDict

from mcp.server.fastmcp import FastMCP

from .chroma_utils import get_chroma_collection
from .tools import datetime_tools

mcp = FastMCP("Thunder Off-Ice KB")
collection = get_chroma_collection()
mcp.mount(datetime_tools.mcp)


class OffIceResult(TypedDict):
    title: str
    category: str
    focus_area: str
    teaching_complexity: str
    progression_stage: str
    description: str
    equipment_needed: Optional[str]
    source_pages: str


@mcp.resource("schema://off_ice", title="Off-Ice Entry Schema")
def get_office_schema() -> str:
    return """{
  \"title\": \"string\",
  \"category\": \"string\",
  \"focus_area\": \"string\",
  \"teaching_complexity\": \"string\",
  \"progression_stage\": \"string\",
  \"description\": \"string\",
  \"equipment_needed\": \"string | null\",
  \"source_pages\": \"string\"
}"""


def _parse_description(doc: str) -> str:
    for line in doc.splitlines():
        if line.lower().startswith("description:"):
            return line.split(":", 1)[1].strip()
    return ""


@mcp.tool("semantic_search_office")
def semantic_search_office(query: str, n_results: int = 5) -> List[OffIceResult]:
    """Semantic search over off-ice training entries."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"source": "off_ice_manual_hockey_canada_level1"},
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    entries: List[OffIceResult] = []
    for doc, meta in zip(docs, metas):
        entries.append(
            {
                "title": meta.get("title", ""),
                "category": meta.get("category", ""),
                "focus_area": meta.get("focus_area", ""),
                "teaching_complexity": meta.get("teaching_complexity", ""),
                "progression_stage": meta.get("progression_stage", ""),
                "description": _parse_description(doc),
                "equipment_needed": meta.get("equipment_needed") or None,
                "source_pages": meta.get("source_pages", ""),
            }
        )
    return entries


if __name__ == "__main__":
    mcp.run(transport="sse")
