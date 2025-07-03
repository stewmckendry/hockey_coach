#!/usr/bin/env python3
"""Download YouTube video audio, transcribe with Whisper, summarize segments."""
import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import List, Dict
import csv
import sys

# Add repo root to PYTHONPATH so `app` package can be imported
sys.path.append(str(Path(__file__).resolve().parent.parent))

import yt_dlp
import whisper

from agents import Runner
from app.client.agent.video_summarizer_agent import video_summarizer_agent, VideoSummaryOutput


# --- Helpers ---
def download_audio(url: str, out_dir: Path) -> tuple[Path, dict]:
    """Download audio using yt-dlp and return file path and video info."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = Path(ydl.prepare_filename(info))
    return filename, info


def transcribe_audio(audio_path: Path) -> dict:
    model = whisper.load_model("base")
    return model.transcribe(str(audio_path))


def group_segments(segments: List[dict], max_words: int = 80) -> List[Dict[str, float | str]]:
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
            chunks.append({"text": " ".join(current_words), "start": start_time, "end": end_time or start_time})
            current_words = words
            start_time = float(seg.get("start", 0))
            end_time = float(seg.get("end", 0))
            word_count = len(words)
        else:
            current_words += words
            end_time = float(seg.get("end", 0))
            word_count += len(words)
    if current_words:
        chunks.append({"text": " ".join(current_words), "start": start_time or 0.0, "end": end_time or (start_time or 0.0)})
    return chunks


async def summarize_chunks(chunks: List[Dict[str, float | str]], title: str) -> List[VideoSummaryOutput]:
    results = []
    for i, chunk in enumerate(chunks):
        text = chunk["text"]
        print(f"\n📝 Summarizing segment {i+1}/{len(chunks)} ({len(text.split())} words)...")
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


async def process_video(url: str, out_json: Path) -> None:
    tmp_dir = Path("tmp_video")
    audio_path, info = download_audio(url, tmp_dir)
    print(f"📥 Downloaded {audio_path}")
    transcript = transcribe_audio(audio_path)
    print("📜 Transcription complete")
    chunks = group_segments(transcript.get("segments", []))
    summaries = await summarize_chunks(chunks, info.get("title", ""))

    clips = []
    for idx, (s, chunk) in enumerate(zip(summaries, chunks)):
        start_time = float(chunk.get("start", 0))
        end_time = float(chunk.get("end", start_time))
        clip = {
            "segment_number": idx + 1,
            "title": info.get("title"),
            "video_url": f"{url}?t={int(start_time)}",
            "source": info.get("uploader"),
            "start_time": start_time,
            "end_time": end_time,
            "summary": s.summary,
            "teaching_points": s.teaching_points,
            "visual_prompt": s.visual_prompt,
            "hockey_skills": s.hockey_skills,
            "position": s.position,
            "complexity": s.complexity,
            "clip_type": s.clip_type,
            "intended_audience": s.intended_audience,
            "play_or_skill_focus": s.play_or_skill_focus,
            "duration": round(end_time - start_time, 2),
            "transcript": chunk["text"],
        }
        clips.append(clip)

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Process YouTube videos into transcripts and summaries")
    parser.add_argument("--url", action="append", required=True, help="YouTube video URL")
    parser.add_argument("--output", type=Path, default=Path("data/processed/video_clips.json"))
    args = parser.parse_args()

    asyncio.run(process_video(args.url[0], args.output))


if __name__ == "__main__":
    main()
