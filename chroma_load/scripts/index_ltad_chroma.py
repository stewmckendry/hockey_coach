#!/usr/bin/env python3
"""Index LTAD skills into a Chroma collection."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from collections import Counter
from datetime import datetime
import sys

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from utils.chroma_utils import get_chroma_collection, clear_chroma_collection


def doc_text(skill: dict) -> str:
    """Create document text for enriched LTAD skill."""
    parts = [
        f"Skill: {skill.get('skill_name') or ''}",
        f"Category: {skill.get('skill_category') or ''}",
        f"Age Group: {skill.get('age_group') or ''}",
        f"Complexity: {skill.get('complexity', '')}",
        f"Summary: {skill.get('summary') or ''}",
        f"Instructions: {skill.get('instructions') or ''}",
        f"Teaching Points: {'; '.join(skill.get('teaching_points') or [])}",
        f"Equipment: {'; '.join(skill.get('equipment') or [])}",
        f"Positions: {'; '.join(skill.get('positions') or [])}",
        f"Source: {skill.get('source') or ''}",
    ]
    text = "\n".join([p for p in parts if p and not p.endswith(': ')])
    return text[:16000]


def metadata_for(skill: dict) -> dict:
    """Create metadata for enriched LTAD skill."""
    def safe_str(val) -> str:
        return val if isinstance(val, str) else ""
    
    def safe_list_str(val) -> str:
        if isinstance(val, list):
            return "; ".join(str(item) for item in val)
        return safe_str(val)
    
    base = {
        "skill_name": safe_str(skill.get("skill_name")),
        "skill_category": safe_str(skill.get("skill_category")),
        "age_group": safe_str(skill.get("age_group")),
        "summary": safe_str(skill.get("summary")),
        "teaching_points": safe_list_str(skill.get("teaching_points")),
        "equipment": safe_list_str(skill.get("equipment")),
        "positions": safe_list_str(skill.get("positions")),
        "complexity": str(skill.get("complexity") or ""),
        "source": safe_str(skill.get("source")),
    }

    return {k: v for k, v in base.items() if v}




def main() -> None:
    parser = argparse.ArgumentParser(description="Index enriched LTAD skills")
    parser.add_argument(
        "--input", type=Path, default=Path("chroma_load/processed"), help="Directory with enriched LTAD skills JSON files"
    )
    parser.add_argument(
        "--file", type=str, help="Specific enriched skills file to index (e.g., enriched_ltad_skills_20250722_143010.json)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing LTAD skills from Chroma collection before indexing",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load and summarize data without indexing to Chroma",
    )
    args = parser.parse_args()

    # Determine input file
    if args.file:
        input_file = Path(args.file)
        if not input_file.is_absolute():
            input_file = args.input / args.file
    else:
        # Find the most recent enriched LTAD skills file
        pattern = "enriched_ltad_skills_*.json"
        files = list(args.input.glob(pattern))
        if not files:
            print(f"❌ No enriched LTAD skills files found in {args.input}")
            print(f"   Looking for pattern: {pattern}")
            return
        input_file = max(files, key=lambda f: f.stat().st_mtime)
        print(f"📂 Using most recent file: {input_file.name}")

    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return

    # Load enriched skills data
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"📊 Loaded {len(data)} enriched skills")
    print(
        "Top categories:",
        Counter(s.get("skill_category") for s in data).most_common(5),
    )
    print(
        "Age group coverage:",
        Counter(s.get("age_group") for s in data).most_common(),
    )
    print(
        "Complexity distribution:",
        Counter(s.get("complexity") for s in data).most_common(),
    )
    print(
        "Position distribution:",
        Counter(pos for s in data for pos in (s.get("positions") or [])).most_common(),
    )

    # Handle Chroma collection
    existing_ids: set[str] = set()
    if args.dry_run:
        print("--dry-run enabled: skipping Chroma indexing")
        collection = None
    else:
        collection = get_chroma_collection()
        existing_ids = set(collection.get().get("ids", []))
        
        # Clear LTAD skills if requested
        if args.clear:
            print("🧹 Clearing existing LTAD skills from Chroma collection...")
            clear_chroma_collection(mode="type", prefix="ltad-")

    # Prepare documents for indexing
    docs, metadatas, ids = [], [], []
    for idx, skill in enumerate(data):
        doc_id = f"ltad-{idx}-{skill.get('skill_name', 'unknown').lower().replace(' ', '-')}"
        if doc_id in existing_ids:
            continue
        meta = metadata_for(skill)
        if not meta:
            print(f"⚠️ Skipping {doc_id}: empty metadata")
            continue
        docs.append(doc_text(skill))
        metadatas.append(meta)
        ids.append(doc_id)

    if docs:
        # Create snapshot for verification
        snapshot = [
            {"id": ids[i], "document": docs[i], "metadata": metadatas[i]}
            for i in range(len(docs))
        ]
        snapshot_file = f"ltad_skills_indexed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(snapshot_file, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
        print(f"📄 Created indexing snapshot: {snapshot_file}")

        if not args.dry_run:
            collection.add(documents=docs, metadatas=metadatas, ids=ids)
            print("Count:", collection.count())
            print(f"✅ Indexed {len(docs)} LTAD skills into Chroma")
        else:
            print(f"✅ Prepared {len(docs)} documents (dry run)")
    else:
        print("No skills to index")


if __name__ == "__main__":
    main()
