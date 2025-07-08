from pathlib import Path
import json
from typing import Optional, List
from typing_extensions import TypedDict
from mcp.server.fastmcp import FastMCP
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadb.config import Settings
import chromadb
import os

# Import video tools so they register with this MCP instance
from . import video_tools  # noqa: F401

mcp = FastMCP("Thunder DrillKB")

# === Drill Schema Definition ===
class Drill(TypedDict):
    title: str
    image_url: Optional[str]
    video_url: Optional[str]
    summary: Optional[str]
    instructions: Optional[str]
    teaching_points: list[str]
    variations: Optional[str]
    tags: list[str]
    position: list[str]
    starting_zone: str
    ending_zone: str
    situation: list[str]
    hockey_skills: list[str]
    complexity: str
    source: str

# Result returned to client
class DrillResult(TypedDict):
    title: str
    link: Optional[str]
    hockey_skills: List[str]
    position: List[str]
    situation: List[str]
    source: str

# === Drill Data Path ===
DRILLS_PATH = Path(__file__).parent.parent / "outputs" / "drills_classified_full.json"

def safe_join(val) -> str:
    if isinstance(val, list):
        return " ".join(val)
    return str(val or "")


#@mcp.tool(title="Search Drills by Keyword")
def search_drills(
    query: str,
    skills: Optional[List[str]] = None,
    position: Optional[List[str]] = None,
    situation: Optional[List[str]] = None
) -> List[DrillResult]:
    """Search hockey drills by keyword (in title, summary, instructions, tags) and optional filters."""
    query_keywords = [q.strip().lower() for q in query.split()] if query else []

    with open(DRILLS_PATH, "r") as f:
        drills = json.load(f)

    results = []
    for d in drills:
        # Build searchable blob
        searchable_text = (
            safe_join(d.get("title")) + " " +
            safe_join(d.get("summary")) + " " +
            safe_join(d.get("instructions")) + " " +
            safe_join(d.get("variations")) + " " +
            safe_join(d.get("teaching_points")) + " " +
            safe_join(d.get("tags")) + " " +
            safe_join(d.get("situation")) + " " +
            safe_join(d.get("hockey_skills"))
        ).lower()

        # Check if all keywords are in searchable blob
        if not all(k in searchable_text for k in query_keywords):
            continue

        # Filter by skills
        if skills:
            drill_skills = set([s.lower() for s in d.get("hockey_skills", [])])
            if not any(s.lower() in drill_skills for s in skills):
                continue

        # Filter by position
        if position:
            drill_pos = set([p.lower() for p in d.get("position", [])])
            if not any(p.lower() in drill_pos for p in position):
                continue

        # Filter by situation
        if situation:
            drill_situ = set([s.lower() for s in d.get("situation", [])])
            if not any(s.lower() in drill_situ for s in situation):
                continue

        # Build short result
        results.append({
            "title": d["title"],
            "link": d.get("video_url") or d.get("image_url"),
            "hockey_skills": d.get("hockey_skills", []),
            "position": d.get("position", []),
            "situation": d.get("situation", []),
            "source": d.get("source", "")
        })

    return results


# === Tool: Get Full Drill by Title ===
@mcp.tool(title="Get Drill by Title")
def get_drill(title: str) -> Optional[Drill]:
    """Look up a drill by exact title."""
    if not title:
        return None

    with open(DRILLS_PATH, "r") as f:
        for drill in json.load(f):
            if drill["title"].strip().lower() == title.strip().lower():
                return drill
    return None

# === Resource: Schema ===
@mcp.resource("schema://drills", title="Drill Metadata Schema")
def get_drill_schema() -> str:
    return """{
  "title": "string",
  "image_url": "string | null",
  "video_url": "string | null",
  "summary": "string | null",
  "instructions": "string | null",
  "teaching_points": "list[string]",
  "variations": "string | null",
  "tags": "list[string]",
  "position": "list[string]",            
  "starting_zone": "string",             
  "ending_zone": "string",               
  "situation": "list[string]",           
  "hockey_skills": "list[string]",       
  "complexity": "string",                
  "source": "string"                     
}"""

# === Tool: Search drills in chroma vector DB ===
from .chroma_utils import get_chroma_collection
collection = get_chroma_collection()

def parse_list(value: str) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(";") if v.strip()]

@mcp.tool(title="Search Drills via Chroma")
def semantic_search_drills(query: str, n_results: int = 5) -> list[DrillResult]:
    """Search for drills using semantic similarity (via vector DB)"""
    results = collection.query(query_texts=[query], n_results=n_results)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    print("🔍 Chroma query returned:", results)

    return [
        {
            "title": meta.get("title", ""),
            "hockey_skills": parse_list(meta.get("hockey_skills", "")),
            "position": parse_list(meta.get("position", "")),
            "situation": parse_list(meta.get("situation", "")),
            "source": meta.get("source", ""),
            "link": meta.get("link", ""),
        }
        for meta in metas
    ]


if __name__ == "__main__":
    mcp.run(transport="sse")

