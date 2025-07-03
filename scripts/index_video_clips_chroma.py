# scripts/index_video_clips_chroma.py
import json
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.mcp_server.chroma_utils import get_chroma_collection, clear_chroma_collection

DATA_PATH = Path(__file__).parent.parent / "data" / "processed" / "video_clips.json"

clear_chroma_collection()
collection = get_chroma_collection()

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)


def clip_text(clip: dict) -> str:
    parts = [
        f"Title: {clip.get('title', '')}",
        f"Summary: {clip.get('summary', '')}",
        "Teaching Points: " + ", ".join(clip.get("teaching_points", [])),
        "Skills: " + ", ".join(clip.get("hockey_skills", [])),
        "Positions: " + ", ".join(clip.get("position", [])),
        f"Complexity: {clip.get('complexity', '')}",
    ]
    return "\n".join(part for part in parts if part)


def metadata_for(clip: dict) -> dict:
    return {
        "title": clip.get("title", ""),
        "summary": clip.get("summary", ""),
        "teaching_points": "; ".join(clip.get("teaching_points", [])),
        "hockey_skills": "; ".join(clip.get("hockey_skills", [])),
        "position": "; ".join(clip.get("position", [])),
        "complexity": clip.get("complexity", ""),
        "source": clip.get("source", ""),
        "video_url": clip.get("video_url", ""),
    }


docs = [clip_text(c) for c in data]
metadatas = [metadata_for(c) for c in data]
ids = [f"video-{i}" for i in range(len(data))]
collection.add(documents=docs, metadatas=metadatas, ids=ids)
print("Count:", collection.count())
results = collection.get(include=["documents", "metadatas"], limit=5)
for i, doc in enumerate(results["documents"]):
    print(f"Doc {i+1}:")
    print("  ID:", results["ids"][i])
    print("  Title:", results["metadatas"][i].get("title"))
    print("  Text:", doc[:100], "...")
print(f"✅ Indexed {len(docs)} video clips into Chroma")
