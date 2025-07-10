# scripts/index_video_clips_chroma.py
import json
import argparse
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from more_itertools import chunked
import tiktoken

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
        f"Video ID: {clip.get('video_id', '')}",
        f"Segment ID: {clip.get('segment_id', '')}",
        f"Query Term: {clip.get('query_term', '')}",
        f"Title: {clip.get('title', '')}",
        f"Summary: {clip.get('summary', '')}",
        clip.get("transcript", ""),
        "Teaching Points: " + ", ".join(clip.get("teaching_points", [])),
        "Skills: " + ", ".join(clip.get("hockey_skills", [])),
        "Positions: " + ", ".join(clip.get("position") or []),
        f"Complexity: {clip.get('complexity', '')}",
        f"Duration: {clip.get('duration', '')}",
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
    def s(val):
        return str(val or "")

    return {
        "segment_number": s(clip.get("segment_number")),
        "segment_id": s(clip.get("segment_id")),
        "video_id": s(clip.get("video_id")),
        "title": s(clip.get("title")),
        "summary": s(clip.get("summary")),
        "query_term": s(clip.get("query_term")),
        "teaching_points": "; ".join(clip.get("teaching_points", [])),
        "hockey_skills": "; ".join(clip.get("hockey_skills", [])),
        "position": "; ".join(clip.get("position") or []),
        "complexity": s(clip.get("complexity")),
        "source": s(clip.get("source")),
        "video_url": s(clip.get("video_url")),
        "start_time": s(clip.get("start_time")),
        "end_time": s(clip.get("end_time")),
        "duration": s(clip.get("duration")),
        "clip_type": s(clip.get("clip_type")),
        "intended_audience": s(clip.get("intended_audience")),
        "play_or_skill_focus": s(clip.get("play_or_skill_focus")),
        "published_at": s(clip.get("published_at")),
        "transcript": clip.get("transcript", "")[:500],
    }

def load_clips(files: list[Path]) -> tuple[list[dict], dict[str, int]]:
    clips: list[dict] = []
    counts: dict[str, int] = {}
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                items = json.load(f)
                clips.extend(items)
                counts[fp.name] = len(items)
                print(f"📂 Loaded {len(items)} clips from {fp}")
        except Exception as e:
            print(f"❌ Failed to load {fp}: {e}")
    return clips, counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Index video clip JSON files into Chroma")
    parser.add_argument("--input-folder", type=Path, help="Folder containing clip JSON files")
    parser.add_argument("--input-files", nargs="*", type=Path, help="Specific clip JSON files")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=100,
        help="Number of clips per indexing chunk",
    )
    args = parser.parse_args()
    chunk_size = args.chunk_size
    enc = tiktoken.get_encoding("cl100k_base")

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

    data, file_counts = load_clips(files)

    docs, metadatas, ids = [], [], []
    video_ids = set()
    query_terms: dict[str, int] = {}
    manifest: dict[str, dict] = {}
    max_tokens = 0

    for clip in data:
        text = clip_text(clip)
        docs.append(text)
        meta = metadata_for(clip)
        metadatas.append(meta)
        tokens = len(enc.encode(text))
        if tokens > max_tokens:
            max_tokens = tokens
        vid_id = clip.get("video_id") or extract_video_id(clip.get("video_url", ""))
        seg_id = clip.get("segment_id") or f"{vid_id}_{clip.get('segment_number', '')}"
        ids.append(f"video-{seg_id}")
        if vid_id:
            video_ids.add(str(vid_id))
            m = manifest.setdefault(str(vid_id), {
                "video_id": str(vid_id),
                "query_term": clip.get("query_term", ""),
                "clip_count": 0,
                "publish_time": clip.get("published_at", "")
            })
            m["clip_count"] += 1
        term = clip.get("query_term")
        if term:
            query_terms[term] = query_terms.get(term, 0) + 1

    if docs:
        print(f"📏 Largest document has {max_tokens} tokens")
        for i, (doc_chunk, meta_chunk, id_chunk) in enumerate(
            zip(
                chunked(docs, chunk_size),
                chunked(metadatas, chunk_size),
                chunked(ids, chunk_size),
            )
        ):
            print(f"📦 Indexing chunk {i+1} with {len(doc_chunk)} clips...")
            try:
                collection.add(documents=doc_chunk, metadatas=meta_chunk, ids=id_chunk)
            except Exception as e:
                print(f"❌ Failed to index chunk {i+1}: {e}")
                continue

        print("Count:", collection.count())
        results = collection.get(include=["documents", "metadatas"], limit=5)
        for i, doc in enumerate(results["documents"]):
            print(f"Doc {i+1}:")
            print("  ID:", results["ids"][i])
            print("  Title:", results["metadatas"][i].get("title"))
            print("  Text:", doc[:100], "...")
        for fname, cnt in file_counts.items():
            print(f"✅ Indexed {cnt} clips from {fname}")
        print(f"Total clips indexed: {len(docs)}")
        print(f"Unique video_id count: {len(video_ids)}")
        if query_terms:
            print("Query term distribution:")
            for term, cnt in query_terms.items():
                print(f"  {term}: {cnt}")

        # Write manifest CSV
        manifest_path = Path("index_manifest.csv")
        import csv
        with open(manifest_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["video_id", "query_term", "clip_count", "publish_time"])
            writer.writeheader()
            writer.writerows(manifest.values())
        summary = {
            "files": file_counts,
            "total_clips": len(docs),
            "unique_videos": len(video_ids),
            "query_terms": query_terms,
        }
        with open("index_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print("✅ Wrote index summary to index_summary.json")
    else:
        print("No clips to index")


if __name__ == "__main__":
    main()
