from __future__ import annotations

"""MCP server exposing off-ice training search tools."""

from typing import List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel
import json
import logging
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from mcp.server.fastmcp import FastMCP

import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.chroma_utils import get_chroma_collection

mcp = FastMCP("Hockey MCP Server")
collection = get_chroma_collection()
client = OpenAI()


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
    instructions: str
    teaching_points: str
    equipment: str
    skills: str
    sub_skills: str
    positions: str
    complexity: str
    source: str
    url: str
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
    age_group: str
    summary: str
    teaching_points: str
    equipment: str
    positions: str
    complexity: str
    source: str
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


class TacticResult(TypedDict):
    tactic_name: str
    summary: str
    instructions: str
    skills: str
    centre_assignments: str
    winger_assignments: str
    defense_assignments: str
    goalie_assignments: str
    teaching_points: str
    source: str
    type: str  # fixed as "tactic"


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


def _get_prefix(doc_id: str) -> str:
    """Return the prefix of a Chroma document ID."""
    return str(doc_id).split("-", 1)[0] if doc_id is not None else ""


@mcp.tool("find_dryland_drills")
def find_dryland_drills(query: str, n_results: int = 5) -> List[OffIceResult]:
    logger.info(
        "find_dryland_drills called with query=%s n_results=%s", query, n_results
    )
    results = collection.query(
        query_texts=[query],
        n_results=n_results * 4,
        where={"source": "off_ice_manual_hockey_canada_level1"},
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    logger.info("find_dryland_drills retrieved %s records from chroma", len(docs))

    entries: List[OffIceResult] = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        prefix = _get_prefix(doc_id)
        logger.info("Processing record id=%s with prefix=%s", doc_id, prefix)
        if not str(doc_id).startswith("dryland-"):
            logger.info("Skipping non-dryland id: %s", doc_id)
            continue
        logger.info("Keeping dryland id: %s", doc_id)
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
        if len(entries) >= n_results:
            break
    if len(entries) < n_results:
        logger.warning(
            "Returned only %s/%s filtered results for tool find_dryland_drills",
            len(entries),
            n_results,
        )
    logger.info("find_dryland_drills response: %s", entries)
    return entries


@mcp.tool("find_dryland_videos")
def find_dryland_videos(query: str, n_results: int = 5) -> List[VideoTitle]:
    """Semantic search over dryland video titles."""
    logger.info(
        "find_dryland_videos called with query=%s n_results=%s", query, n_results
    )
    results = collection.query(
        query_texts=[query],
        n_results=n_results * 4,
        where={"type": "off_ice_video"},
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    logger.info("find_dryland_videos retrieved %s records from chroma", len(docs))
    video_results: List[dict] = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        prefix = _get_prefix(doc_id)
        logger.info("Processing record id=%s with prefix=%s", doc_id, prefix)
        if not str(doc_id).startswith("dryland-"):
            logger.info("Skipping non-dryland id: %s", doc_id)
            continue
        logger.info("Keeping dryland id: %s", doc_id)
        video_results.append(
            {
                "video_id": meta.get("video_id", ""),
                "title": meta.get("title", ""),
                "video_url": meta.get("video_url", ""),
                "document": doc,
                "metadata": meta,
            }
        )
        if len(video_results) >= n_results:
            break
    if len(video_results) < n_results:
        logger.warning(
            "Returned only %s/%s filtered results for tool find_dryland_videos",
            len(video_results),
            n_results,
        )
    logger.info("find_dryland_videos response: %s", video_results)
    return video_results


@mcp.tool("find_hockey_drills")
def find_hockey_drills(query: str, n_results: int = 5) -> List[DrillResult]:
    logger.info(
        "find_hockey_drills called with query=%s n_results=%s", query, n_results
    )
    results = collection.query(query_texts=[query], n_results=n_results * 4)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    logger.info("find_hockey_drills retrieved %s records from chroma", len(docs))

    drills: List[DrillResult] = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        prefix = _get_prefix(doc_id)
        logger.info("Processing record id=%s with prefix=%s", doc_id, prefix)
        if not str(doc_id).startswith("drill-"):
            logger.info("Skipping non-drill id: %s", doc_id)
            continue
        logger. info("Keeping drill id: %s", doc_id)
        drills.append(
            {
                "title": meta.get("title", ""),
                "summary": meta.get("summary", ""),
                "instructions": meta.get("instructions", ""),
                "teaching_points": meta.get("teaching_points", ""),
                "equipment": meta.get("equipment", ""),
                "skills": meta.get("skills", ""),
                "sub_skills": meta.get("sub_skills", ""),
                "positions": meta.get("positions", ""),
                "complexity": meta.get("complexity", ""),
                "source": meta.get("source", ""),
                "url": meta.get("url", ""),
                "type": "on_ice_drill",
            }
        )
        if len(drills) >= n_results:
            break
    if len(drills) < n_results:
        logger.warning(
            "Returned only %s/%s filtered results for tool find_hockey_drills",
            len(drills),
            n_results,
        )
    logger.info("Final drill result titles: %s", [d["title"] for d in drills])
    logger.info("find_hockey_drills response: %s", drills)
    return drills


@mcp.tool("find_hockey_videos")
def find_hockey_videos(query: str, n_results: int = 5) -> List[VideoClipResult]:
    logger.info(
        "find_hockey_videos called with query=%s n_results=%s", query, n_results
    )
    results = collection.query(
        query_texts=[query],
        n_results=n_results * 4,
        where={"clip_type": {"$ne": "off_ice_video"}},
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    logger.info("find_hockey_videos retrieved %s records from chroma", len(docs))

    clips: List[VideoClipResult] = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        prefix = _get_prefix(doc_id)
        logger.info("Processing record id=%s with prefix=%s", doc_id, prefix)
        if not str(doc_id).startswith("video-"):
            logger.info("Skipping non-video id: %s", doc_id)
            continue
        logger.info("Keeping video id: %s", doc_id)
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
    if len(clips) < n_results:
        logger.warning(
            "Returned only %s/%s filtered results for tool find_hockey_videos",
            len(clips),
            n_results,
        )
    logger.info("find_hockey_videos response: %s", clips)
    return clips


@mcp.tool("find_hockey_skills")
def find_hockey_skills(query: str, n_results: int = 5) -> List[LTADSkillResult]:
    logger.info(
        "find_hockey_skills called with query=%s n_results=%s", query, n_results
    )
    results = collection.query(query_texts=[query], n_results=n_results * 4)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    logger.info("find_hockey_skills retrieved %s records from chroma", len(docs))

    skills: List[LTADSkillResult] = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        prefix = _get_prefix(doc_id)
        logger.info("Processing record id=%s with prefix=%s", doc_id, prefix)
        if not str(doc_id).startswith("ltad-"):
            logger.info("Skipping non-ltad id: %s", doc_id)
            continue
        logger.info("Keeping ltad id: %s", doc_id)
        skills.append(
            {
                "skill_name": meta.get("skill_name", ""),
                "skill_category": meta.get("skill_category", ""),
                "age_group": meta.get("age_group", ""),
                "summary": meta.get("summary", ""),
                "teaching_points": meta.get("teaching_points", ""),
                "equipment": meta.get("equipment", ""),
                "positions": meta.get("positions", ""),
                "complexity": meta.get("complexity", ""),
                "source": meta.get("source", ""),
                "type": "ltad_skill",
            }
        )
        if len(skills) >= n_results:
            break
    if len(skills) < n_results:
        logger.warning(
            "Returned only %s/%s filtered results for tool find_hockey_skills",
            len(skills),
            n_results,
        )
    logger.info("find_hockey_skills response: %s", skills)
    return skills


@mcp.tool("find_nhl_interviews")
def find_nhl_interviews(query: str, n_results: int = 5) -> List[NHLInsight]:
    logger.info(
        "find_nhl_interviews called with query=%s n_results=%s", query, n_results
    )
    results = collection.query(query_texts=[query], n_results=n_results * 4)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    logger.info("find_nhl_interviews retrieved %s records from chroma", len(docs))

    insights: List[NHLInsight] = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        prefix = _get_prefix(doc_id)
        logger.info("Processing record id=%s with prefix=%s", doc_id, prefix)
        if not str(doc_id).startswith("insight-"):
            logger.info("Skipping non-insight id: %s", doc_id)
            continue
        logger.info("Keeping insight id: %s", doc_id)
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
    if len(insights) < n_results:
        logger.warning(
            "Returned only %s/%s filtered results for tool find_nhl_interviews",
            len(insights),
            n_results,
        )
    logger.info("find_nhl_interviews response: %s", insights)
    return insights


@mcp.tool("find_hockey_tactics")
def find_hockey_tactics(query: str, n_results: int = 5) -> List[TacticResult]:
    logger.info(
        "find_hockey_tactics called with query=%s n_results=%s", query, n_results
    )
    results = collection.query(query_texts=[query], n_results=n_results * 4)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    logger.info("find_hockey_tactics retrieved %s records from chroma", len(docs))

    tactics: List[TacticResult] = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        prefix = _get_prefix(doc_id)
        logger.info("Processing record id=%s with prefix=%s", doc_id, prefix)
        if not str(doc_id).startswith("tactic_"):
            logger.info("Skipping non-tactic id: %s", doc_id)
            continue
        logger.info("Keeping tactic id: %s", doc_id)
        tactics.append(
            {
                "tactic_name": meta.get("tactic_name", ""),
                "summary": meta.get("summary", ""),
                "instructions": _parse_field(doc, "Instructions"),
                "skills": meta.get("skills", ""),
                "centre_assignments": meta.get("centre_assignments", ""),
                "winger_assignments": meta.get("winger_assignments", ""),
                "defense_assignments": meta.get("defense_assignments", ""),
                "goalie_assignments": meta.get("goalie_assignments", ""),
                "teaching_points": meta.get("teaching_points", ""),
                "source": meta.get("source", ""),
                "type": "tactic",
            }
        )
        if len(tactics) >= n_results:
            break
    if len(tactics) < n_results:
        logger.warning(
            "Returned only %s/%s filtered results for tool find_hockey_tactics",
            len(tactics),
            n_results,
        )
    logger.info("find_hockey_tactics response: %s", tactics)
    return tactics

@mcp.tool("find_hockey_rules")
def find_hockey_rules(query: str, n_results: int = 5) -> List[ConductPolicy]:
    logger.info("find_hockey_rules called with query=%s n_results=%s", query, n_results)
    results = collection.query(
        query_texts=[query],
        n_results=n_results * 4,
        where={"type": "conduct_policy"},
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    logger.info("find_hockey_rules retrieved %s records from chroma", len(docs))

    policies: List[ConductPolicy] = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        prefix = _get_prefix(doc_id)
        logger.info("Processing record id=%s with prefix=%s", doc_id, prefix)
        if not str(doc_id).startswith("conduct-"):
            logger.info("Skipping non-conduct id: %s", doc_id)
            continue
        logger.info("Keeping conduct id: %s", doc_id)
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
        if len(policies) >= n_results:
            break
    if len(policies) < n_results:
        logger.warning(
            "Returned only %s/%s filtered results for tool find_hockey_rules",
            len(policies),
            n_results,
        )
    logger.info("find_hockey_rules response: %s", policies)
    return policies


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(mcp.sse_app, host="0.0.0.0", port=8000)
