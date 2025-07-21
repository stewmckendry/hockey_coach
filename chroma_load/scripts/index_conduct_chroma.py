#!/usr/bin/env python3
"""Index conduct entries into a Chroma collection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.mcp_server.chroma_utils import get_chroma_collection


def doc_text(entry: dict) -> str:
    return f"{entry.get('title','')}\n{entry.get('content','')}"[:16000]


def metadata_for(entry: dict) -> dict:
    def s(val) -> str:
        return val if isinstance(val, str) else ""
    return {
        "role": s(entry.get("role")),
        "topic": s(entry.get("topic")),
        "document_type": s(entry.get("document_type")),
        "source": s(entry.get("source")),
        "page": str(entry.get("page") or ""),
        "type": "conduct_policy",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Index conduct entries")
    parser.add_argument("--input", type=Path, default=Path("data/processed/conduct_enriched.json"), help="Path to conduct_enriched.json")
    parser.add_argument("--dry-run", action="store_true", help="Print summary without indexing")
    parser.add_argument("--limit", type=int, help="Only index first N entries")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.limit:
        data = data[: args.limit]
    print(f"📂 Loaded {len(data)} entries from {args.input}")

    collection = get_chroma_collection()
    existing = set(collection.get().get("ids", []))

    indexed = 0
    skipped = 0

    for idx, entry in enumerate(data):
        doc_id = f"conduct-{idx}"
        title = entry.get("title") or ""
        content = entry.get("content") or ""

        if doc_id in existing:
            print(f"⏭️  Skipping {doc_id}: already indexed")
            skipped += 1
            continue

        if not (title and content):
            print(f"⚠️ Skipping {doc_id}: missing title or content")
            skipped += 1
            continue

        print(f"Indexing {doc_id}: {title}")
        if args.dry_run:
            indexed += 1
            continue

        try:
            collection.add(documents=[doc_text(entry)], metadatas=[metadata_for(entry)], ids=[doc_id])
            indexed += 1
        except Exception as e:
            print(f"❌ Failed to index {doc_id}: {e}")
            skipped += 1

    print(f"✅ Indexed {indexed} entries, skipped {skipped}")
    try:
        print("Final collection count:", collection.count())
    except Exception as e:
        print(f"❌ Could not retrieve collection count: {e}")


if __name__ == "__main__":
    main()
