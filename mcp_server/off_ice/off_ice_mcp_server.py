from __future__ import annotations

"""MCP server exposing off-ice training search tools."""

from typing import List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel
import json
from openai import OpenAI

from mcp.server.fastmcp import FastMCP

import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent.parent))
from chroma_utils import get_chroma_collection

mcp = FastMCP("Off-Ice KB MCP Server")
collection = get_chroma_collection()
client = OpenAI()

from datetime_tools import get_current_date
mcp.tool(get_current_date)

class OffIceResult(TypedDict):
    title: str
    category: str
    focus_area: str
    teaching_complexity: str
    progression_stage: str
    description: str
    equipment_needed: Optional[str]
    source_pages: str


class CategorySummary(BaseModel):
    category: str
    summary: str

class VideoTitle(TypedDict):
    video_id: str
    title: str
    video_url: str
    document: str
    metadata: dict


class VideoClip(TypedDict):
    video_id: str
    title: str
    start_time: str
    end_time: str
    summary: str | None
    transcript: str | None
    complexity: str | None


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


@mcp.tool("find_dryland_drills")
def find_dryland_drills(query: str, n_results: int = 5) -> List[OffIceResult]:
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


@mcp.tool("find_dryland_videos")
def find_dryland_videos(query: str, n_results: int = 5) -> List[VideoTitle]:
    """Semantic search over dryland video titles."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"type": "off_ice_video"},
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    video_results: List[dict] = []
    for doc, meta in zip(docs, metas):
        video_results.append({
            "video_id": meta.get("video_id", ""),
            "title": meta.get("title", ""),
            "video_url": meta.get("video_url", ""),
            "document": doc,
            "metadata": meta,
        })
    return video_results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.sse_app, host="0.0.0.0", port=8000)


