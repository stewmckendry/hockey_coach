#!/usr/bin/env python3
"""Index LTAD skills into a Chroma collection."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import os
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.mcp_server.chroma_utils import get_client, _embed


def doc_text(skill: dict) -> str:
    parts = [
        f"Age Group: {skill.get('age_group', '')}",
        f"Stage: {skill.get('ltad_stage', '')}",
        f"Position: {', '.join(skill.get('position', []))}",
        f"Category: {skill.get('skill_category', '')}",
        f"Skill: {skill.get('skill_name', '')}",
        skill.get("teaching_notes", ""),
        f"Month: {skill.get('season_month', '')}",
    ]
    text = "\n".join([p for p in parts if p])
    return text[:16000]


def metadata_for(skill: dict) -> dict:
    return {
        "age_group": skill.get("age_group", ""),
        "ltad_stage": skill.get("ltad_stage", ""),
        "position": "; ".join(skill.get("position", [])),
        "skill_category": skill.get("skill_category", ""),
        "skill_name": skill.get("skill_name", ""),
        "teaching_notes": skill.get("teaching_notes", ""),
        "season_month": skill.get("season_month", ""),
        "source": skill.get("source", ""),
    }


def clear_collection(coll) -> None:
    ids = coll.get().get("ids", [])
    if ids:
        coll.delete(ids=ids)
        print(f"🧹 Cleared {len(ids)} documents")


def main() -> None:
    parser = argparse.ArgumentParser(description="Index normalized LTAD skills")
    parser.add_argument(
        "--input", type=Path, default=Path("data/processed/ltad_index.json"), help="Normalized skills JSON"
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
