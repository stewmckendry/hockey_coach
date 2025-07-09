#!/usr/bin/env python3
"""Analyze LTAD skills dataset and write summary statistics to Markdown."""

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


def counts_by_source(skills: List[dict]) -> Dict[str, Dict[str, int]]:
    """Return counts of skills by source and category."""
    result: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for skill in skills:
        src = skill.get("source", "Unknown") or "Unknown"
        cat = skill.get("skill_category", "Unknown") or "Unknown"
        result[src][cat] += 1
    return result


def completeness_by_source(skills: List[dict]) -> Dict[str, Dict[str, float]]:
    """Calculate data completeness for each source."""
    grouped: Dict[str, List[dict]] = defaultdict(list)
    for skill in skills:
        src = skill.get("source", "Unknown") or "Unknown"
        grouped[src].append(skill)
    return {src: completeness(items) for src, items in grouped.items()}


def render_markdown(
    counts: Dict[str, Dict[str, int]],
    lists: Dict[str, Dict[str, List[str]]],
    stats: Dict[str, float],
    src_counts: Dict[str, Dict[str, int]],
    src_stats: Dict[str, Dict[str, float]],
) -> str:
    """Return full markdown report for all analysis."""
    lines: List[str] = ["# LTAD Skills Analysis"]

    lines.append("\n## Skill Counts by Age Group and Category")
    for age in sorted(counts):
        lines.append(f"\n### Age Group: {age}")
        total = 0
        for category, cnt in sorted(counts[age].items()):
            lines.append(f"- **{category}**: {cnt}")
            total += cnt
        lines.append(f"- **Total**: {total}")

    lines.append("\n## Skill Names by Age Group and Category")
    for age in sorted(lists):
        lines.append(f"\n### Age Group: {age}")
        for category, names in sorted(lists[age].items()):
            joined = ", ".join(sorted(set(names)))
            lines.append(f"- **{category}**: {joined}")

    lines.append("\n## Data Completeness (Overall)")
    lines.append("| Field | % Complete |")
    lines.append("|-------|------------|")
    for field, pct in stats.items():
        lines.append(f"| {field} | {pct:.1f}% |")

    lines.append("\n## Analysis by Source")
    for src in sorted(src_counts):
        total = sum(src_counts[src].values())
        lines.append(f"\n### Source: {src} (Total: {total} skills)")
        lines.append("#### Counts by Category")
        for cat, cnt in sorted(src_counts[src].items()):
            lines.append(f"- **{cat}**: {cnt}")

        comp = src_stats.get(src, {})
        lines.append("\n#### Data Completeness")
        lines.append("| Field | % Complete |")
        lines.append("|-------|------------|")
        for field, pct in comp.items():
            lines.append(f"| {field} | {pct:.1f}% |")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze LTAD skills dataset")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/ltad_skills_processed.json"),
        help="Input JSON file with LTAD skills",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/ltad_skill_analysis.md"),
        help="Markdown file to write analysis",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"❌ File not found: {args.input}")
        return

    skills = load_skills(args.input)
    print(f"✅ Loaded {len(skills)} skills from {args.input}")

    counts = summary_counts(skills)
    print("✅ Generated summary counts")

    lists = skill_lists_by_age(skills)
    print("✅ Generated skill lists")

    stats = completeness(skills)
    print("✅ Calculated data completeness")

    src_counts = counts_by_source(skills)
    src_stats = completeness_by_source(skills)
    print("✅ Analyzed skills by source")

    md = render_markdown(counts, lists, stats, src_counts, src_stats)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(md, encoding="utf-8")
    print(f"✅ Wrote analysis to {args.output}")


if __name__ == "__main__":
    main()
