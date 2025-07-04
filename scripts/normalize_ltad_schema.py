#!/usr/bin/env python3
"""Normalize LTAD skill JSON into a consistent schema."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import List

from pydantic import BaseModel


class LTADSkill(BaseModel):
    age_group: str
    ltad_stage: str | None = None
    position: List[str]
    skill_category: str
    skill_name: str
    teaching_notes: str
    season_month: str | None = None
    source: str


SYNONYMS = {
    "crossunders": "crossovers",
    "goalie": "goaltending",
}


def normalize_entry(item: dict) -> dict:
    item = {k: v for k, v in item.items() if v is not None}
    item.setdefault("position", ["Any"])
    item.setdefault("age_group", "Unknown")

    item["position"] = [SYNONYMS.get(p.lower(), p).title() for p in item.get("position", [])]
    item["skill_category"] = SYNONYMS.get(item.get("skill_category", "").lower(), item.get("skill_category", "")).title()
    item["skill_name"] = SYNONYMS.get(item.get("skill_name", "").lower(), item.get("skill_name", "")).title()
    return item


def deduplicate(items: List[dict]) -> List[dict]:
    seen = set()
    result = []
    for it in items:
        key = (
            it.get("age_group"),
            ";".join(it.get("position", [])),
            it.get("skill_category"),
            it.get("skill_name"),
            it.get("season_month"),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(it)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize LTAD skill JSON")
    parser.add_argument(
        "--input", type=Path, default=Path("data/processed/ltad_skills_raw.json"), help="Raw skills JSON"
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/processed/ltad_index.json"), help="Normalized output JSON"
    )
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = [normalize_entry(d) for d in data]
    deduped = deduplicate(cleaned)
    skills = [LTADSkill(**d).model_dump() for d in deduped]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(skills, f, indent=2)
    print(f"✅ Wrote {len(skills)} normalized skills to {args.output}")


if __name__ == "__main__":
    main()
