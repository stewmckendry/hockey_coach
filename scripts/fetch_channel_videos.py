#!/usr/bin/env python3
"""Fetch a list of videos from a YouTube channel using yt-dlp."""
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

import yt_dlp


def fetch_videos(channel_url: str) -> List[Dict[str, Any]]:
    """Return basic metadata for all videos in the channel."""
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)

    entries = info.get("entries", []) or []
    videos: List[Dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        url = e.get("url")
        if url and not url.startswith("http"):
            url = f"https://www.youtube.com/watch?v={e.get('id')}"
        videos.append(
            {
                "title": e.get("title"),
                "url": url,
                "view_count": e.get("view_count"),
                "published_date": e.get("upload_date") or e.get("release_date") or e.get("timestamp"),
            }
        )
    return videos


def filter_videos(videos: List[Dict[str, Any]], keywords: List[str] | None) -> List[Dict[str, Any]]:
    if not keywords:
        return videos
    out: List[Dict[str, Any]] = []
    for v in videos:
        title = v.get("title", "").lower()
        if any(k.lower() in title for k in keywords):
            out.append(v)
    return out


def sort_videos(videos: List[Dict[str, Any]], mode: str | None) -> None:
    if mode == "recent":
        videos.sort(key=lambda x: x.get("published_date") or "", reverse=True)
    elif mode == "popular":
        videos.sort(key=lambda x: x.get("view_count") or 0, reverse=True)


def write_output(videos: List[Dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix == ".json":
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(videos, f, indent=2)
    else:
        with open(out_path, "w", encoding="utf-8") as f:
            for v in videos:
                if v.get("url"):
                    f.write(v["url"] + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch YouTube channel videos")
    parser.add_argument("--channel", required=True, help="YouTube channel URL or handle")
    parser.add_argument("--sort", choices=["recent", "popular"], help="Sort videos")
    parser.add_argument("--limit", type=int, help="Limit number of videos")
    parser.add_argument("--filter", dest="keywords", action="append", help="Filter by keyword in title (repeatable)")
    parser.add_argument("--output", type=Path, default=Path("data/input/channel_videos.txt"), help="Output file (.txt or .json)")
    args = parser.parse_args()

    try:
        videos = fetch_videos(args.channel)
    except Exception as e:
        print(f"❌ Failed to fetch channel videos: {e}")
        return

    total = len(videos)
    videos = filter_videos(videos, args.keywords)
    sort_videos(videos, args.sort)
    if args.limit:
        videos = videos[: args.limit]

    print(f"📺 Retrieved {len(videos)} of {total} videos")
    write_output(videos, args.output)
    print(f"✅ Saved results to {args.output}")


if __name__ == "__main__":
    main()
