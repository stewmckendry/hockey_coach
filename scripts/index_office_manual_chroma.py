#!/usr/bin/env python3
"""Index enriched off-ice manual entries into a Chroma collection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

import sys

# Add repo root to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.mcp_server.chroma_utils import get_chroma_collection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def doc_text(entry: dict) -> str:
    parts = [
        f"Title: {entry.get('title')}",
        f"Category: {entry.get('category')}",
        f"Focus: {entry.get('focus_area')}",
        f"Progression Stage: {entry.get('progression_stage')}",
        f"Complexity: {entry.get('teaching_complexity')}",
        f"Equipment: {entry.get('equipment_needed')}",
        f"Description: {entry.get('description')}",
        f"Safety Notes: {entry.get('safety_notes') or ''}",
    ]
    return "\n".join(p for p in parts if p)


def metadata_for(entry: dict) -> dict:
    return {
        "title": entry.get("title"),
        "category": entry.get("category"),
        "focus_area": entry.get("focus_area"),
        "progression_stage": entry.get("progression_stage"),
        "teaching_complexity": entry.get("teaching_complexity"),
        "equipment_needed": entry.get("equipment_needed"),
        "age_recommendation": entry.get("age_recommendation"),
        "source_pages": entry.get("source_pages"),
        "source": entry.get("source", "off_ice_manual_hockey_canada_level1"),
        "type": "off_ice_training",
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Index off-ice entries into Chroma")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/off_ice_enriched.json"),
        help="Path to off_ice_enriched.json",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print summary without indexing")
    parser.add_argument("--limit", type=int, help="Only index first N entries")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data: List[dict] = json.load(f)
    except FileNotFoundError:
        print(f"❌ Input file not found: {args.input}")
        return

    if args.limit:
        data = data[: args.limit]
    print(f"📂 Loaded {len(data)} entries from {args.input}")

    collection = get_chroma_collection()
    existing = set(collection.get().get("ids", []))
    indexed = 0
    skipped = 0

    for idx, entry in enumerate(data):
        doc_id = f"office-{idx}"
        title = entry.get("title") or ""

        if doc_id in existing:
            print(f"⏭️  Skipping {doc_id}: already indexed")
            skipped += 1
            continue

        if not (entry.get("title") and entry.get("description") and entry.get("category")):
            print(f"⚠️ Skipping {doc_id}: missing required fields")
            skipped += 1
            continue

        print(f"Indexing {doc_id}: {title}")
        if args.dry_run:
            indexed += 1
            continue

        try:
            collection.add(
                documents=[doc_text(entry)],
                metadatas=[metadata_for(entry)],
                ids=[doc_id],
            )
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
