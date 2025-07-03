import json
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict

# === CONFIG ===
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_PATH = SCRIPT_DIR.parent / "outputs" / "drills_classified_full.json"
OUT_DIR = SCRIPT_DIR.parent / "analysis"
OUT_DIR.mkdir(exist_ok=True)

# === LOAD DATA ===
with open(INPUT_PATH, "r") as f:
    drills = json.load(f)

print(f"📥 Loaded {len(drills)} drills")

# === Fields to Check
FIELDS = [
    "title", "image_url", "video_url", "instructions",
    "summary", "teaching_points", "variations", "tags",
    "position", "starting_zone", "ending_zone", "situation",
    "hockey_skills", "complexity"
]

SOURCES = sorted(set(d.get("source", "Unknown") for d in drills))

# === Field Completeness per Source
completeness_data = []

for source in SOURCES:
    source_drills = [d for d in drills if d.get("source") == source]
    row = {"source": source, "total_drills": len(source_drills)}
    for field in FIELDS:
        non_empty = sum(1 for d in source_drills if d.get(field))
        row[f"{field}_non_empty"] = non_empty
    completeness_data.append(row)

completeness_df = pd.DataFrame(completeness_data)
completeness_df.to_csv(OUT_DIR / "field_completeness_by_source.csv", index=False)
print("📤 Saved field completeness to: field_completeness_by_source.csv")

# === Value Diversity per Source (e.g. for position, skills, complexity)
def count_flat_values(drills, field):
    counter = Counter()
    for d in drills:
        val = d.get(field)
        if isinstance(val, list):
            counter.update(val)
        elif isinstance(val, str) and val.strip():
            counter[val.strip()] += 1
    return dict(counter)

value_breakdowns = {}

for source in SOURCES:
    source_drills = [d for d in drills if d.get("source") == source]
    field_counts = {}
    for field in ["position", "starting_zone", "ending_zone", "situation", "hockey_skills", "complexity", "tags"]:
        counts = count_flat_values(source_drills, field)
        field_counts[field] = counts
    value_breakdowns[source] = field_counts

with open(OUT_DIR / "value_distributions_by_source.json", "w") as f:
    json.dump(value_breakdowns, f, indent=2)

print("📤 Saved value distributions to: value_distributions_by_source.json")
