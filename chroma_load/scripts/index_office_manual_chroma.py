#!/usr/bin/env python3
"""Index enriched off-ice manual entries into a Chroma collection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

import sys

# Add repo root to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from utils.chroma_utils import get_chroma_collection, clear_chroma_collection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def doc_text(entry: dict) -> str:
    """Create document text for enriched off-ice workout."""
    parts = [
        f"Title: {entry.get('title', '')}",
        f"Category: {entry.get('category', '')}",
        f"Summary: {entry.get('summary', '')}",
        f"Instructions: {entry.get('instructions', '')}",
        f"Teaching Points: {'; '.join(entry.get('teaching_points', []))}",
        f"Equipment: {entry.get('equipment', '')}",
        f"Complexity: {entry.get('complexity', '')}",
        f"Source: {entry.get('source', '')}",
    ]
    text = "\n".join([p for p in parts if p and not p.endswith(': ') and not p.endswith(': N/A')])
    return text[:16000]

def metadata_for(entry: dict) -> dict:
    """Create metadata for enriched off-ice workout."""
    def safe_str(value) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            return "; ".join(str(v) for v in value)
        return str(value)

    return {
        "title": safe_str(entry.get("title")),
        "category": safe_str(entry.get("category")),
        "summary": safe_str(entry.get("summary")),
        "instructions": safe_str(entry.get("instructions")),
        "teaching_points": safe_str(entry.get("teaching_points")),
        "equipment": safe_str(entry.get("equipment")),
        "complexity": safe_str(entry.get("complexity")),
        "source": safe_str(entry.get("source", "off_ice_manual_hockey_canada_level1")),
        "age_recommendation": safe_str(entry.get("age_recommendation")),
        "source_page": safe_str(entry.get("source_page")),
        "document_type": "off_ice_workout"
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Index enriched off-ice workouts into Chroma")
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to enriched off-ice JSON file (default: find latest in processed/dryland/)"
    )
    parser.add_argument(
        "--clear-office",
        action="store_true", 
        help="Clear existing off-ice documents (with 'office-' prefix) before indexing"
    )
    parser.add_argument("--dry-run", action="store_true", help="Print summary without indexing")
    parser.add_argument("--limit", type=int, help="Only index first N entries")
    args = parser.parse_args()

    # Determine input file
    if args.input:
        input_file = args.input
    else:
        # Find latest enriched off-ice file
        processed_dir = Path(__file__).parent.parent / "processed" / "dryland"
        enriched_files = list(processed_dir.glob("off_ice_enriched_*.json"))
        
        if enriched_files:
            # Use the most recent enriched file
            input_file = max(enriched_files, key=lambda p: p.stat().st_mtime)
            print(f"📂 Using most recent enriched off-ice file: {input_file}")
        else:
            # Fall back to legacy location
            input_file = Path("data/processed/off_ice_enriched.json")
            print(f"📂 Using legacy off-ice file: {input_file}")

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data: List[dict] = json.load(f)
    except FileNotFoundError:
        print(f"❌ Input file not found: {input_file}")
        print("   Run the off-ice enrichment script first or specify --input")
        return

    if args.limit:
        data = data[: args.limit]
    print(f"📂 Loaded {len(data)} enriched off-ice workouts from {input_file}")

    # Clear existing off-ice documents if requested
    if args.clear_office:
        print("🧹 Clearing existing off-ice documents...")
        clear_chroma_collection(mode="type", prefix="office-")

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

        if not (entry.get("title") and entry.get("summary") and entry.get("category")):
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
