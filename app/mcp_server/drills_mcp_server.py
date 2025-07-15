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
# Use absolute import to avoid ImportError when running as a script
import video_tools  # noqa: F401

mcp = FastMCP("Drills MCP Server")

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

