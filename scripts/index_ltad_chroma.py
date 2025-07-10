#!/usr/bin/env python3
"""Index LTAD skills into a Chroma collection."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.mcp_server.chroma_utils import get_client, _embed


def doc_text(skill: dict) -> str:
    ags = ', '.join(skill.get('age_groups') or [])
    parts = [
        f"Age Groups: {ags}",
        f"Stage: {skill.get('ltad_stage') or ''}",
        f"Position: {', '.join(skill.get('position') or [])}",
        f"Category: {skill.get('skill_category') or ''}",
        f"Skill: {skill.get('skill_name') or ''}",
        skill.get("teaching_notes") or "",
        f"Month: {skill.get('season_month') or ''}",
    ]
    text = "\n".join([p for p in parts if p])
    return text[:16000]


def metadata_for(skill: dict) -> dict:
    def safe_str(val) -> str:
        return val if isinstance(val, str) else ""

    return {
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


def clear_collection(coll) -> None:
    ids = coll.get().get("ids", [])
    if ids:
        coll.delete(ids=ids)
        print(f"🧹 Cleared {len(ids)} documents")


def main() -> None:
    parser = argparse.ArgumentParser(description="Index normalized LTAD skills")
    parser.add_argument(
        "--input", type=Path, default=Path("data/processed/ltad_skills_final.json"), help="Normalized skills JSON"
    )
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    client = get_client()
    collection = client.get_or_create_collection("ltad_index", embedding_function=_embed)
    clear_collection(collection)

    docs, metadatas, ids = [], [], []
    for idx, skill in enumerate(data):
        docs.append(doc_text(skill))
        metadatas.append(metadata_for(skill))
        ids.append(f"ltad-{idx}")

    if docs:
        collection.add(documents=docs, metadatas=metadatas, ids=ids)
        print("Count:", collection.count())
        print(f"✅ Indexed {len(docs)} LTAD skills into Chroma")
    else:
        print("No skills to index")


if __name__ == "__main__":
    main()
