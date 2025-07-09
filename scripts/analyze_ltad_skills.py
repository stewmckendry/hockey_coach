#!/usr/bin/env python3
"""Analyze LTAD skills dataset and print summary statistics."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List


FIELDS = [
    "age_group",
    "ltad_stage",
    "position",
    "skill_category",
    "skill_name",
    "teaching_notes",
    "season_month",
    "progression_stage",
    "teaching_complexity",
    "variant",
    "source",
]


def load_skills(path: Path) -> List[dict]:
    """Load skills JSON from path."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def summary_counts(skills: List[dict]) -> Dict[str, Dict[str, int]]:
    counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for skill in skills:
        age = skill.get("age_group", "Unknown") or "Unknown"
        category = skill.get("skill_category", "Unknown") or "Unknown"
        counts[age][category] += 1
    return counts


def skill_lists_by_age(skills: List[dict]) -> Dict[str, Dict[str, List[str]]]:
    lists: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    for skill in skills:
        age = skill.get("age_group", "Unknown") or "Unknown"
        category = skill.get("skill_category", "Unknown") or "Unknown"
        name = skill.get("skill_name", "").strip()
        if name:
            lists[age][category].append(name)
    return lists


def completeness(skills: List[dict]) -> Dict[str, float]:
    totals = {field: 0 for field in FIELDS}
    for skill in skills:
        for field in FIELDS:
            val = skill.get(field)
            if val is None:
                continue
            if isinstance(val, list):
                if val:
                    totals[field] += 1
            elif isinstance(val, str):
                if val.strip():
                    totals[field] += 1
            else:
                totals[field] += 1
    total_records = len(skills) if skills else 1
    return {field: round(totals[field] / total_records * 100, 2) for field in FIELDS}


def print_summary(counts: Dict[str, Dict[str, int]]) -> None:
    print("\n--- Skill Counts by Age Group and Category ---")
    for age in sorted(counts):
        print(f"\nAge Group: {age}")
        total = 0
        for category, count in sorted(counts[age].items()):
            print(f"  {category}: {count}")
            total += count
        print(f"  Total: {total}")


def print_skill_lists(lists: Dict[str, Dict[str, List[str]]]) -> None:
    print("\n--- Skill Names by Age Group and Category ---")
    for age in sorted(lists):
        print(f"\nAge Group: {age}")
        for category, names in sorted(lists[age].items()):
            joined = ", ".join(sorted(set(names)))
            print(f"  {category}: {joined}")


def print_completeness(stats: Dict[str, float]) -> None:
    print("\n--- Data Completeness (% of records with value) ---")
    for field, pct in stats.items():
        print(f"{field}: {pct:.1f}%")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze LTAD skills dataset")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/ltad_skills_processed.json"),
        help="Input JSON file with LTAD skills",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"❌ File not found: {args.input}")
        return

    skills = load_skills(args.input)
    print(f"✅ Loaded {len(skills)} skills from {args.input}")

    counts = summary_counts(skills)
    print_summary(counts)
    print("✅ Generated summary counts")

    lists = skill_lists_by_age(skills)
    print_skill_lists(lists)
    print("✅ Generated skill lists")

    stats = completeness(skills)
    print_completeness(stats)
    print("✅ Calculated data completeness")


if __name__ == "__main__":
    main()
