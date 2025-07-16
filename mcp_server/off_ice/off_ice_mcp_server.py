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

from tools.datetime_tools import get_current_date
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


class SequencePhase(BaseModel):
    phase: str
    category: str
    description: str


class FocusAreaProgression(BaseModel):
    focus_area: str
    summary: str


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


@mcp.tool("summarize_office_by_category")
def summarize_office_by_category(n_per_category: int = 5) -> List[CategorySummary]:
    """Summarize indexed off-ice entries grouped by category."""
    data = collection.get(
        where={"source": "off_ice_manual_hockey_canada_level1"},
        include=["documents", "metadatas"],
    )
    categories: dict[str, list[tuple[str, dict]]] = {}
    docs = data.get("documents", [])
    metas = data.get("metadatas", [])
    for doc, meta in zip(docs, metas):
        cat = (meta.get("category") or "").strip()
        if not cat:
            continue
        categories.setdefault(cat, []).append((doc, meta))

    summaries: List[CategorySummary] = []
    for cat, items in categories.items():
        entries_text = ""
        for doc, meta in items[:n_per_category]:
            desc = _parse_description(doc)
            title = meta.get("title", "")
            stage = meta.get("progression_stage", "")
            entries_text += f"Title: {title}\nStage: {stage}\n{desc}\n\n"

        system_prompt = (
            "You are an expert off-ice hockey trainer. Summarize what this "
            "category trains, when drills are best used during a session, and "
            "how difficulty progresses across stages."
        )
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Category: {cat}\n\n" + entries_text},
            ],
        )
        summary = resp.choices[0].message.content.strip()
        summaries.append(CategorySummary(category=cat, summary=summary))

    return summaries


@mcp.tool("get_recommended_sequence")
def get_recommended_sequence(prompt: str) -> List[SequencePhase]:
    """Generate a structured session sequence from a natural language prompt."""
    results = collection.query(
        query_texts=[prompt],
        n_results=15,
        where={"source": "off_ice_manual_hockey_canada_level1"},
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    grouped: dict[str, list[str]] = {}
    for doc, meta in zip(docs, metas):
        cat = meta.get("category", "")
        stage = meta.get("progression_stage", "")
        key = f"{cat} | {stage}"
        grouped.setdefault(key, []).append(_parse_description(doc))

    text = ""
    for key, descs in grouped.items():
        text += f"{key}\n" + "\n".join(f"- {d}" for d in descs) + "\n\n"

    system_prompt = (
        "Use the grouped drills below to create a phased off-ice session "
        "sequence. Return JSON list of objects with fields: phase, category, "
        "description."
    )
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
    )
    content = resp.choices[0].message.content.strip()
    try:
        phases = json.loads(content)
    except Exception:
        return []
    return [SequencePhase(**p) for p in phases]


STAGE_ORDER = {"Introductory": 0, "Developmental": 1, "Refinement": 2}


@mcp.tool("get_progressions_for_focus_area")
def get_progressions_for_focus_area(focus_area: str) -> FocusAreaProgression:
    """Summarize the progression path for a given focus area."""
    data = collection.get(
        where={
            "$and": [
                {"focus_area": focus_area},
                {"source": "off_ice_manual_hockey_canada_level1"},
            ]
        },
        include=["documents", "metadatas"],
    )
    docs = data.get("documents", [])
    metas = data.get("metadatas", [])

    entries = sorted(
        zip(metas, docs),
        key=lambda x: STAGE_ORDER.get(x[0].get("progression_stage", ""), 99),
    )
    text = ""
    for meta, doc in entries:
        stage = meta.get("progression_stage", "")
        title = meta.get("title", "")
        text += f"Stage: {stage}\nTitle: {title}\n{_parse_description(doc)}\n\n"

    system_prompt = (
        "Provide an overview of how this skill progresses from introductory to "
        "advanced. Mention example drills for each stage."
    )
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
    )
    summary = resp.choices[0].message.content.strip()
    return FocusAreaProgression(focus_area=focus_area, summary=summary)


if __name__ == "__main__":
    mcp.run(transport="sse")
