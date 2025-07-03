# scripts/index_video_clips_chroma.py
import json
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.mcp_server.chroma_utils import (
    get_chroma_collection,
    clear_chroma_collection,
)

DATA_PATH = Path(__file__).parent.parent / "data" / "processed" / "video_clips.json"

# Wipe only existing video documents so drills remain intact
clear_chroma_collection(mode="type", prefix="video-")
collection = get_chroma_collection()

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)


def clip_text(clip: dict) -> str:
    """Assemble a text block for embedding."""
    parts = [
        f"Title: {clip.get('title', '')}",
        f"Summary: {clip.get('summary', '')}",
        clip.get("transcript", ""),
        "Teaching Points: " + ", ".join(clip.get("teaching_points", [])),
        "Skills: " + ", ".join(clip.get("hockey_skills", [])),
        "Positions: " + ", ".join(clip.get("position") or []),
        f"Complexity: {clip.get('complexity', '')}",
        f"Clip Type: {clip.get('clip_type', '')}",
        f"Audience: {clip.get('intended_audience', '')}",
        f"Focus: {clip.get('play_or_skill_focus', '')}",
    ]
    text = "\n".join(part for part in parts if part)
    # Ensure we don't embed extremely long documents
    if len(text) > 16000:
        text = text[:16000]
    return text


def metadata_for(clip: dict) -> dict:
    """Flatten clip fields for easier filtering/search."""
    return {
        "segment_number": str(clip.get("segment_number", "")),
        "title": clip.get("title", ""),
        "summary": clip.get("summary", ""),
        "teaching_points": "; ".join(clip.get("teaching_points", [])),
        "hockey_skills": "; ".join(clip.get("hockey_skills", [])),
        "position": "; ".join(clip.get("position") or []),
        "complexity": clip.get("complexity", ""),
        "source": clip.get("source", ""),
        "video_url": clip.get("video_url", ""),
        "start_time": str(clip.get("start_time", "")),
        "end_time": str(clip.get("end_time", "")),
        "duration": str(clip.get("duration", "")),
        "clip_type": clip.get("clip_type", ""),
        "intended_audience": clip.get("intended_audience", ""),
        "play_or_skill_focus": clip.get("play_or_skill_focus", ""),
        "transcript": clip.get("transcript", "")[:500],
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
