# scripts/index_drills_chroma.py
import os
import json
from pathlib import Path
from typing import List

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from dotenv import load_dotenv

load_dotenv()

# Setup Chroma client
import sys
sys.path.append(str(Path(__file__).parent.parent / "mcp_server"))
from chroma_utils import get_chroma_collection, clear_chroma_collection

clear_chroma_collection()

collection = get_chroma_collection()

# === Load classified drills ===
DATA_PATH = Path(__file__).parent.parent / "data" / "processed" / "drills.json"
with open(DATA_PATH, "r") as f:
    data = json.load(f)

# === Build text chunks to embed ===
def drill_text(drill: dict) -> str:
    def join_list(label, items):
        return f"{label}: {', '.join(items)}" if items else ""

    parts = [
        f"Title: {drill.get('title', '')}",
        f"Instructions: {drill.get('instructions', '')}",
        f"Summary: {drill.get('summary', '')}",
        join_list("Teaching Points", drill.get("teaching_points", [])),
        join_list("Variations", drill.get("variations", [])),
        join_list("Tags", drill.get("tags", [])),
        join_list("Skills", drill.get("hockey_skills", [])),
        join_list("Situations", drill.get("situation", [])),
        join_list("Position", drill.get("position", [])),
        f"Starting Zone: {drill.get('starting_zone', '')}",
        f"Ending Zone: {drill.get('ending_zone', '')}",
        f"Complexity: {drill.get('complexity', '')}",
        f"Source: {drill.get('source', '')}",
    ]
    return "\n".join(part for part in parts if part)

# === Prepare metadata (flatten lists to comma-separated strings) ===
def safe_str(value) -> str:
    return value if isinstance(value, str) else ""

def metadata_for(drill: dict) -> dict:
    return {
        "title": safe_str(drill.get("title")),
        "summary": safe_str(drill.get("summary")),
        "instructions": safe_str(drill.get("instructions")),
        "teaching_points": "; ".join(drill.get("teaching_points", [])),
        "variations": "; ".join(drill.get("variations", [])),
        "tags": "; ".join(drill.get("tags", [])),
        "hockey_skills": "; ".join(drill.get("hockey_skills", [])),
        "situation": "; ".join(drill.get("situation", [])),
        "position": "; ".join(drill.get("position", [])),
        "starting_zone": safe_str(drill.get("starting_zone")),
        "ending_zone": safe_str(drill.get("ending_zone")),
        "complexity": safe_str(drill.get("complexity")),
        "source": safe_str(drill.get("source")),
    }


# === Index drills ===
docs = [drill_text(d) for d in data]
metadatas = [metadata_for(d) for d in data]
ids = [f"drill-{i}" for i in range(len(data))]

collection.add(documents=docs, metadatas=metadatas, ids=ids)
print("Count:", collection.count())
results = collection.get(include=["documents", "metadatas"], limit=5)
for i, doc in enumerate(results["documents"]):
    print(f"Doc {i+1}:")
    print("  ID:", results["ids"][i])  # this is always included even if not in `include`
    print("  Title:", results["metadatas"][i].get("title"))
    print("  Text:", doc[:100], "...")
print(f"✅ Indexed {len(docs)} drills into Chroma")
