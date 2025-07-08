#!/usr/bin/env python3
"""Download YouTube video audio, transcribe with Whisper, summarize segments."""
import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import List, Dict, Set
import csv
import sys

# Add repo root to PYTHONPATH so `app` package can be imported
sys.path.append(str(Path(__file__).resolve().parent.parent))

import yt_dlp
from urllib.parse import urlparse, parse_qs
import whisper

from agents import Runner
from app.client.agent.video_summarizer_agent import (
    video_summarizer_agent,
    VideoSummaryOutput,
)
from tools.youtube_search_tool import get_video_metadata


# --- Helpers ---
def parse_video_id(url: str) -> str | None:
    """Extract the YouTube video ID from a URL if possible."""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if "youtu.be" in host:
        return parsed.path.lstrip("/")
    if "youtube.com" in host:
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]
        if parsed.path.startswith("/watch"):
            # fallback: parse from path or full URL
            return parsed.query.split("&")[0].replace("v=", "")
    return None


def download_audio(url: str, out_dir: Path) -> tuple[Path, dict]:
    """Download audio using yt-dlp and return file path and video metadata."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = Path(ydl.prepare_filename(info))

    video_id = parse_video_id(url) or info.get("id")
    try:
        meta = get_video_metadata(video_id)
        info = meta.model_dump()
        info["id"] = video_id
        info["uploader"] = meta.author
    except Exception:
        info = {"id": video_id, "title": None, "uploader": None}

    return filename, info


def transcribe_audio(audio_path: Path) -> dict:
    model = whisper.load_model("base")
    return model.transcribe(str(audio_path))


def group_segments(
    segments: List[dict], max_words: int = 80
) -> List[Dict[str, float | str]]:
    """Group whisper segments into larger text chunks while preserving timestamps."""
    chunks: List[Dict[str, float | str]] = []
    current_words: List[str] = []
    start_time: float | None = None
    end_time: float | None = None
    word_count = 0
    for seg in segments:
        words = seg["text"].split()
        if start_time is None:
            start_time = float(seg.get("start", 0))
        if word_count + len(words) > max_words and current_words:
            chunks.append(
                {
                    "text": " ".join(current_words),
                    "start": start_time,
                    "end": end_time or start_time,
                }
            )
            current_words = words
            start_time = float(seg.get("start", 0))
            end_time = float(seg.get("end", 0))
            word_count = len(words)
        else:
            current_words += words
            end_time = float(seg.get("end", 0))
            word_count += len(words)
    if current_words:
        chunks.append(
            {
                "text": " ".join(current_words),
                "start": start_time or 0.0,
                "end": end_time or (start_time or 0.0),
            }
        )
    return chunks


async def summarize_chunks(
    chunks: List[Dict[str, float | str]], title: str
) -> List[VideoSummaryOutput]:
    results = []
    for i, chunk in enumerate(chunks):
        text = chunk["text"]
        print(
            f"\n📝 Summarizing segment {i+1}/{len(chunks)} ({len(text.split())} words)..."
        )
        agent_input = f"Video Title: {title}\nTranscript Segment:\n{text}"
        try:
            run = await Runner.run(video_summarizer_agent, agent_input)
            summary = run.final_output_as(VideoSummaryOutput)
        except Exception as e:
            print(f"❌ Agent call failed: {e}")
            continue
        print(f"✅ Segment {i+1} summarized")
        print(summary.model_dump_json(indent=2))
        results.append(summary)
    return results


async def process_video(url: str, output: Path, separate: bool = False) -> int:
    """Process a single YouTube URL and write clips to disk.

    If ``separate`` is True, ``output`` should be a folder and the JSON/CSV files
    will be created inside it using ``video_id`` in the filename. Otherwise
    ``output`` is treated as a combined JSON file.
    Returns the number of clips processed.
    """
    tmp_dir = Path("tmp_video")
    audio_path, info = download_audio(url, tmp_dir)
    print(f"📥 Downloaded {audio_path}")
    transcript = transcribe_audio(audio_path)
    print("📜 Transcription complete")
    chunks = group_segments(transcript.get("segments", []))
    summaries = await summarize_chunks(chunks, info.get("title", ""))

    video_id = info.get("id", "unknown")

    clips = []
    for idx, (s, chunk) in enumerate(zip(summaries, chunks)):
        start_time = float(chunk.get("start", 0))
        end_time = float(chunk.get("end", start_time))
        position = s.position or []
        if not position:
            position = ["Any"]

        clip = {
            "segment_number": idx + 1,
            "segment_id": f"{video_id}_{idx+1:03d}".lower(),
            "video_id": video_id,
            "title": info.get("title"),
            "video_url": f"{url}?t={int(start_time)}",
            "source": info.get("uploader"),
            "start_time": start_time,
            "end_time": end_time,
            "summary": s.summary,
            "teaching_points": s.teaching_points,
            "visual_prompt": s.visual_prompt,
            "hockey_skills": s.hockey_skills,
            "position": position,
            "complexity": s.complexity,
            "clip_type": s.clip_type,
            "intended_audience": s.intended_audience,
            "play_or_skill_focus": s.play_or_skill_focus,
            "duration": round(end_time - start_time, 2),
            "transcript": chunk["text"],
        }
        clips.append(clip)
    out_json = output
    if separate:
        output.mkdir(parents=True, exist_ok=True)
        out_json = output / f"video_clips_{video_id}.json"

    existing = []
    if out_json.exists():
        with open(out_json, "r", encoding="utf-8") as f:
            existing = json.load(f)
    existing.extend(clips)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)
    print(f"✅ Wrote {len(clips)} clips to {out_json}")

    # Bonus: also export CSV for spreadsheet users
    csv_path = out_json.with_suffix(".csv")
    fieldnames = list(clips[0].keys()) if clips else []
    if fieldnames:
        if csv_path.exists():
            with open(csv_path, "r", encoding="utf-8") as f:
                pass  # ensure file exists for append
        write_header = not csv_path.exists()
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerows(clips)
        print(f"✅ Appended clips to {csv_path}")

    return len(clips)


async def run_all(args) -> None:
    urls: list[str] = args.url or []
    if args.url_file:
        if args.url_file.suffix == ".json":
            try:
                with open(args.url_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data:
                    if isinstance(item, str):
                        urls.append(item)
                    elif isinstance(item, dict) and item.get("url"):
                        urls.append(item["url"])
            except Exception as e:
                print(f"⚠️ Failed to load JSON URLs: {e}")
        else:
            with open(args.url_file, "r", encoding="utf-8") as f:
                urls.extend([ln.strip() for ln in f if ln.strip()])

    if not urls:
        print("No URLs provided. Use --url or --url-file.")
        return

    separate = bool(args.output_folder)
    output_path = args.output_folder if separate else args.output

    processed_ids: Set[str] = set()
    if not separate and output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            for clip in existing:
                vid = clip.get("video_id") or parse_video_id(clip.get("video_url", ""))
                if vid:
                    processed_ids.add(vid)
        except Exception as e:
            print(f"⚠️ Could not read existing clips from {output_path}: {e}")

    summary = []
    for url in urls:
        vid = parse_video_id(url)
        if not args.force and vid and vid in processed_ids:
            print(f"⏭️  Skipping {url} (already processed)")
            summary.append((url, 0, "skipped"))
            continue

        print(f"\n==== Processing {url} ====")
        try:
            count = await process_video(url, output_path, separate)
            summary.append((url, count, None))
            if vid:
                processed_ids.add(vid)
        except Exception as e:
            print(f"❌ Failed to process {url}: {e}")
            summary.append((url, 0, str(e)))

    print("\n--- Summary ---")
    for url, count, err in summary:
        if err:
            print(f"❌ {url} failed: {err}")
        else:
            print(f"✅ {url} -> {count} clips")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Process YouTube videos into transcripts and summaries"
    )
    parser.add_argument(
        "--url", action="append", help="YouTube video URL (repeat for multiple)"
    )
    parser.add_argument(
        "--url-file",
        type=Path,
        dest="url_file",
        help="Text file with YouTube URLs, one per line",
    )
    parser.add_argument(
        "--url-list", type=Path, dest="url_file", help="Alias of --url-file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/video_clips.json"),
        help="Combined output JSON",
    )
    parser.add_argument(
        "--output-folder",
        type=Path,
        help="Folder to write separate JSON files per video",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocess videos even if already processed",
    )
    args = parser.parse_args()

    asyncio.run(run_all(args))


if __name__ == "__main__":
    main()
