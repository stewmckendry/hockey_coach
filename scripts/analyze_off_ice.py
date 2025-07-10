import json
import os
from collections import Counter

INPUT_FILE = "data/processed/off_ice_enriched.json"
OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "off_ice_enriched_summary.md")

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_records = len(data)
    category_counts = Counter()
    for rec in data:
        category = rec.get("category", "Unknown")
        category_counts[category] += 1

    lines = []
    lines.append("# Off-Ice Enriched Summary\n")
    lines.append(f"- **Total records:** {total_records}\n")
    lines.append("## Records by Category\n")
    for cat, count in category_counts.items():
        lines.append(f"- **{cat}:** {count}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write('\n'.join(lines))

    print(f"Summary written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()