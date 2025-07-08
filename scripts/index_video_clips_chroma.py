# scripts/index_video_clips_chroma.py
import json
import argparse
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.mcp_server.chroma_utils import (
    get_chroma_collection,
    clear_chroma_collection,
)

def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from a URL safely."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    # Case 1: Standard YouTube link with ?v=abc123
    if "v" in qs:
        return qs["v"][0]

    # Case 2: Shortened youtu.be links
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")

    # Case 3: If it’s a /watch path but v= is missing
    if parsed.path.startswith("/watch") and "v" in parsed.query:
        return parsed.query.split("&")[0].replace("v=", "")

    # Fallback: Warn and return None
    print(f"⚠️ Warning: Could not extract video ID from URL: {url}")
    return None



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
        "segment_id": clip.get("segment_id", ""),
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
        "intended_audience": str(clip.get("intended_audience") or ""),
        "play_or_skill_focus": clip.get("play_or_skill_focus", ""),
        "transcript": clip.get("transcript", "")[:500],
    }

def load_clips(files: list[Path]) -> list[dict]:
    clips: list[dict] = []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                items = json.load(f)
                clips.extend(items)
                print(f"📂 Loaded {len(items)} clips from {fp}")
        except Exception as e:
            print(f"❌ Failed to load {fp}: {e}")
    return clips


def main() -> None:
    parser = argparse.ArgumentParser(description="Index video clip JSON files into Chroma")
    parser.add_argument("--input-folder", type=Path, help="Folder containing clip JSON files")
    parser.add_argument("--input-files", nargs="*", type=Path, help="Specific clip JSON files")
    args = parser.parse_args()

    files: list[Path] = []
    if args.input_folder:
        files.extend(sorted(Path(args.input_folder).glob("*.json")))
    if args.input_files:
        files.extend(args.input_files)
    if not files:
        files = [Path(__file__).parent.parent / "data" / "processed" / "video_clips.json"]

    # Wipe only existing video documents so drills remain intact
    clear_chroma_collection(mode="type", prefix="video-")
    collection = get_chroma_collection()

    data = load_clips(files)

    docs, metadatas, ids = [], [], []
    for clip in data:
        docs.append(clip_text(clip))
        metadatas.append(metadata_for(clip))
        vid_id = clip.get("video_id") or extract_video_id(clip.get("video_url", ""))
        seg_id = clip.get("segment_id") or f"{vid_id}_{clip.get('segment_number', '')}"
        ids.append(f"video-{seg_id}")

    if docs:
        collection.add(documents=docs, metadatas=metadatas, ids=ids)
        print("Count:", collection.count())
        results = collection.get(include=["documents", "metadatas"], limit=5)
        for i, doc in enumerate(results["documents"]):
            print(f"Doc {i+1}:")
            print("  ID:", results["ids"][i])
            print("  Title:", results["metadatas"][i].get("title"))
            print("  Text:", doc[:100], "...")
        print(f"✅ Indexed {len(docs)} video clips into Chroma")
    else:
        print("No clips to index")


if __name__ == "__main__":
    main()
