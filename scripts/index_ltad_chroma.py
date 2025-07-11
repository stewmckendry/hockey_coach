#!/usr/bin/env python3
"""Index LTAD skills into a Chroma collection."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from collections import Counter
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.mcp_server.chroma_utils import get_chroma_collection


def doc_text(skill: dict) -> str:
    ags = ", ".join(skill.get("age_groups") or [])
    parts = [
        f"Age Groups: {ags}",
        f"Stage: {skill.get('ltad_stage') or ''}",
        f"Position: {', '.join(skill.get('position') or [])}",
        f"Category: {skill.get('skill_category') or ''}",
        f"Skill: {skill.get('skill_name') or ''}",
        f"Variant: {skill.get('variant') or ''}",
        f"Complexity: {skill.get('teaching_complexity') or ''}",
        skill.get("teaching_notes") or "",
        f"Month: {skill.get('season_month') or ''}",
    ]
    text = "\n".join([p for p in parts if p])
    return text[:16000]


def metadata_for(skill: dict) -> dict:
    def safe_str(val) -> str:
        return val if isinstance(val, str) else ""
    base = {
        "age_groups": "; ".join(skill.get("age_groups") or []),
        "ltad_stage": safe_str(skill.get("ltad_stage")),
        "position": "; ".join(skill.get("position") or []),
        "skill_category": safe_str(skill.get("skill_category")),
        "skill_name": safe_str(skill.get("skill_name")),
        "teaching_notes": safe_str(skill.get("teaching_notes")),
        "season_month": safe_str(skill.get("season_month")),
        "progression_stage": safe_str(skill.get("progression_stage")),
        "teaching_complexity": str(skill.get("teaching_complexity") or ""),
        "variant": safe_str(skill.get("variant")),
        "source": safe_str(skill.get("source")),
    }

    return {k: v for k, v in base.items() if v}




def main() -> None:
    parser = argparse.ArgumentParser(description="Index normalized LTAD skills")
    parser.add_argument(
        "--input", type=Path, default=Path("data/processed/ltad_skills_final.json"), help="Normalized skills JSON"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load and summarize data without indexing to Chroma",
    )
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(
        "Top categories:",
        Counter(s.get("skill_category") for s in data).most_common(5),
    )
    print(
        "Age group coverage:",
        Counter(g for s in data for g in (s.get("age_groups") or [])).most_common(),
    )

    existing_ids: set[str] = set()
    if args.dry_run:
        print("--dry-run enabled: skipping Chroma indexing")
        collection = None
    else:
        collection = get_chroma_collection()
        existing_ids = set(collection.get().get("ids", []))

    docs, metadatas, ids = [], [], []
    for idx, skill in enumerate(data):
        doc_id = f"ltad-{idx}"
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
        snapshot = [
            {"id": ids[i], "document": docs[i], "metadata": metadatas[i]}
            for i in range(len(docs))
        ]
        with open("ltad_skills_indexed.json", "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)

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
