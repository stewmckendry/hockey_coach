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
        lines.append(f"- **# of skills by skill category:**")
        for cat, count in info["by_category"].items():
            lines.append(f"  - {cat}: {count}")
        lines.append(f"- **# of skills by position:**")
        for pos, count in info["by_position"].items():
            lines.append(f"  - {pos}: {count}")
        lines.append(f"- **List of skills by skill category:**")
        for cat, skills in info["skills_by_category"].items():
            skill_list = ', '.join(sorted(set(skills)))
            lines.append(f"  - {cat}: {skill_list}")

    lines.append("\n## Incomplete Metadata Records\n")
    if incomplete:
        lines.append("| Index | Skill Name | Missing Fields |")
        lines.append("|-------|------------|---------------|")
        for idx, name, missing in incomplete:
            lines.append(f"| {idx} | {name} | {', '.join(missing)} |")
    else:
        lines.append("All records have complete metadata.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write('\n'.join(lines))

    print(f"Summary written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()