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


class DrillResult(TypedDict):
    title: str
    summary: str
    teaching_points: str
    skills: str
    tags: str
    position: str
    starting_zone: str
    ending_zone: str
    complexity: str
    source: str
    type: str  # fixed as "on_ice_drill"


class VideoClipResult(TypedDict):
    title: str
    summary: str
    hockey_skills: str
    teaching_points: str
    play_or_skill_focus: str
    complexity: str
    clip_type: str
    intended_audience: str
    video_url: str
    duration: str
    type: str  # fixed as "general_video"


class LTADSkillResult(TypedDict):
    skill_name: str
    skill_category: str
    teaching_notes: str
    age_groups: str
    complexity: str
    variant: str
    position: str
    progression_stage: str
    season_month: str
    type: str  # fixed as "ltad_skill"


class NHLInsight(TypedDict):
    speaker: str
    quote: str
    question: str
    tags: str
    takeaways_for_coach: str
    takeaways_for_player: str
    source_url: str
    published_date: str
    type: str  # fixed as "nhl_insight"


class ConductPolicy(TypedDict):
    title: str
    topic: str
    role: str
    document_type: str
    content: str
    source: str
    type: str  # fixed as "conduct_policy"


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


def _parse_field(doc: str, label: str) -> str:
    """Extract a value for ``label`` from an indexed document."""
    prefix = label.lower() + ":"
    for line in doc.splitlines():
        if line.lower().startswith(prefix):
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


@mcp.tool("find_hockey_drills")
def find_hockey_drills(query: str, n_results: int = 5) -> List[DrillResult]:
    results = collection.query(query_texts=[query], n_results=n_results)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]

    drills: List[DrillResult] = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        if not str(doc_id).startswith("drill-"):
            continue
        drills.append(
            {
                "title": meta.get("title", ""),
                "summary": meta.get("summary", ""),
                "teaching_points": meta.get("teaching_points", ""),
                "skills": meta.get("hockey_skills", ""),
                "tags": meta.get("tags", ""),
                "position": meta.get("position", ""),
                "starting_zone": meta.get("starting_zone", ""),
                "ending_zone": meta.get("ending_zone", ""),
                "complexity": meta.get("complexity", ""),
                "source": meta.get("source", ""),
                "type": "on_ice_drill",
            }
        )
        if len(drills) >= n_results:
            break
    return drills


@mcp.tool("find_hockey_videos")
def find_hockey_videos(query: str, n_results: int = 5) -> List[VideoClipResult]:
    results = collection.query(query_texts=[query], n_results=n_results)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]

    clips: List[VideoClipResult] = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        if meta.get("clip_type") == "off_ice_video":
            continue
        clips.append(
            {
                "title": meta.get("title", ""),
                "summary": meta.get("summary", ""),
                "hockey_skills": meta.get("hockey_skills", ""),
                "teaching_points": meta.get("teaching_points", ""),
                "play_or_skill_focus": meta.get("play_or_skill_focus", ""),
                "complexity": meta.get("complexity", ""),
                "clip_type": meta.get("clip_type", ""),
                "intended_audience": meta.get("intended_audience", ""),
                "video_url": meta.get("video_url", ""),
                "duration": meta.get("duration", ""),
                "type": "general_video",
            }
        )
        if len(clips) >= n_results:
            break
    return clips


@mcp.tool("find_hockey_skills")
def find_hockey_skills(query: str, n_results: int = 5) -> List[LTADSkillResult]:
    results = collection.query(query_texts=[query], n_results=n_results)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]

    skills: List[LTADSkillResult] = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        if not str(doc_id).startswith("ltad-"):
            continue
        skills.append(
            {
                "skill_name": meta.get("skill_name", ""),
                "skill_category": meta.get("skill_category", ""),
                "teaching_notes": meta.get("teaching_notes", ""),
                "age_groups": meta.get("age_groups", ""),
                "complexity": meta.get("teaching_complexity", ""),
                "variant": meta.get("variant", ""),
                "position": meta.get("position", ""),
                "progression_stage": meta.get("progression_stage", ""),
                "season_month": meta.get("season_month", ""),
                "type": "ltad_skill",
            }
        )
        if len(skills) >= n_results:
            break
    return skills


@mcp.tool("find_nhl_interviews")
def find_nhl_interviews(query: str, n_results: int = 5) -> List[NHLInsight]:
    results = collection.query(query_texts=[query], n_results=n_results)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]

    insights: List[NHLInsight] = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        if not str(doc_id).startswith("insight-"):
            continue
        insights.append(
            {
                "speaker": meta.get("speaker", ""),
                "quote": _parse_field(doc, "Quote"),
                "question": meta.get("question", ""),
                "tags": meta.get("tags", ""),
                "takeaways_for_coach": _parse_field(doc, "Takeaways (Coach)"),
                "takeaways_for_player": _parse_field(doc, "Takeaways (Player)"),
                "source_url": meta.get("source_url", ""),
                "published_date": meta.get("published_date", ""),
                "type": "nhl_insight",
            }
        )
        if len(insights) >= n_results:
            break
    return insights


@mcp.tool("find_hockey_rules")
def find_hockey_rules(query: str, n_results: int = 5) -> List[ConductPolicy]:
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"type": "conduct_policy"},
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    policies: List[ConductPolicy] = []
    for doc, meta in zip(docs, metas):
        policies.append(
            {
                "title": meta.get("title", ""),
                "topic": meta.get("topic", ""),
                "role": meta.get("role", ""),
                "document_type": meta.get("document_type", ""),
                "content": doc,
                "source": meta.get("source", ""),
                "type": "conduct_policy",
            }
        )
    return policies


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.sse_app, host="0.0.0.0", port=8000)


