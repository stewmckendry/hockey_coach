#!/usr/bin/env python3
"""Sanity check LTAD skill JSON before indexing."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import List

REQUIRED_FIELDS = ["skill_name", "skill_category", "teaching_notes", "source"]


def load_skills(path: Path) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_skill(skill: dict, idx: int) -> bool:
    errors: List[str] = []
    for field in REQUIRED_FIELDS:
        val = skill.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            errors.append(f"missing {field}")
    tc = skill.get("teaching_complexity")
    if tc is not None and not isinstance(tc, int):
        errors.append("teaching_complexity must be int or null")
    pos = skill.get("position")
    if pos is not None and not isinstance(pos, list):
        errors.append("position must be a list or null")
    if errors:
        print(f"❌ Skill {idx}: {', '.join(errors)}")
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate LTAD skill JSON")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/ltad_skills_final.json"),
        help="Path to skill JSON file",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"❌ File not found: {args.input}")
        return

    skills = load_skills(args.input)
    valid = 0
    for idx, skill in enumerate(skills, 1):
        if validate_skill(skill, idx):
            valid += 1
    print(f"✅ {valid}/{len(skills)} skills passed validation")


if __name__ == "__main__":
    main()
