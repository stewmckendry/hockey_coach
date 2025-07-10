#!/usr/bin/env python3
import json
from uuid import uuid4
from pathlib import Path

INPUT_PATH = Path("data/processed/mlhs_insights.json")
OUTPUT_PATH = INPUT_PATH  # overwrite same file

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    insights = json.load(f)

existing_ids = set()
for insight in insights:
    original_id = insight.get("id", "")
    if not original_id or original_id in existing_ids or not str(original_id).startswith("insight-"):
        insight["id"] = f"insight-{uuid4()}"
    existing_ids.add(insight["id"])

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(insights, f, indent=2)

print(f"✅ Rewrote {len(insights)} insights with fresh insight IDs to {OUTPUT_PATH}")
