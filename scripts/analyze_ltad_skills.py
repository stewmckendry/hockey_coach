import json
import os
from collections import defaultdict, Counter

INPUT_FILE = "data/processed/ltad_skills_postprocessed.json"
OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ltad_skills_summary.md")

def get_age_groups(record):
    # Handles both "age_group" (str) and "age_groups" (list)
    if "age_groups" in record and isinstance(record["age_groups"], list):
        return record["age_groups"]
    elif "age_group" in record and record["age_group"]:
        return [record["age_group"]]
    else:
        return ["Unknown"]

def get_positions(record):
    # Handles both "position" (list) and missing
    if "position" in record and isinstance(record["position"], list):
        return record["position"]
    else:
        return ["Unknown"]

def get_skill_category(record):
    return record.get("skill_category", "Unknown")

def get_skill_name(record):
    return record.get("skill_name", "Unknown")

def check_metadata(record):
    required_fields = [
        "age_group", "ltad_stage", "position", "skill_category", "skill_name", "teaching_notes", "source"
    ]
    missing = [f for f in required_fields if f not in record or not record[f]]
    return missing

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_records = len(data)

    # Age group summary
    age_group_counts = Counter()
    skills_by_age_group = defaultdict(list)
    for rec in data:
        for age in get_age_groups(rec):
            age_group_counts[age] += 1
            skills_by_age_group[age].append(rec)

    # Details for each age group
    details = {}
    for age, records in skills_by_age_group.items():
        cat_counter = Counter()
        pos_counter = Counter()
        skills_by_cat = defaultdict(list)
        for rec in records:
            cat = get_skill_category(rec)
            pos_list = get_positions(rec)
            cat_counter[cat] += 1
            for pos in pos_list:
                pos_counter[pos] += 1
            skills_by_cat[cat].append(get_skill_name(rec))
        details[age] = {
            "by_category": cat_counter,
            "by_position": pos_counter,
            "skills_by_category": skills_by_cat
        }

    # Metadata completeness
    incomplete = []
    for idx, rec in enumerate(data):
        missing = check_metadata(rec)
        if missing:
            incomplete.append((idx, get_skill_name(rec), missing))
    completeness = 100.0 * (1 - len(incomplete) / total_records) if total_records else 0

    # Write markdown
    lines = []
    lines.append(f"# LTAD Skills Summary\n")
    lines.append(f"- **Total skill records:** {total_records}\n")
    lines.append(f"- **Metadata completeness:** {completeness:.1f}% ({total_records - len(incomplete)}/{total_records} complete)\n")

    lines.append("\n## Skill Records by Age Group\n")
    for age, count in age_group_counts.items():
        lines.append(f"- **{age}:** {count}")

    for age, info in details.items():
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
        default=Path("data/processed/ltad_skills_final.json"),
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