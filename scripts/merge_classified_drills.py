import json
from pathlib import Path

# === CONFIG ===
SCRIPT_DIR = Path(__file__).resolve().parent
FULL_OUTPUT = SCRIPT_DIR.parent / "outputs" / "drills_classified_full.json"
UNIFIED_OUTPUT = SCRIPT_DIR.parent / "outputs" / "drills_classified_merged.json"
UNCLASSIFIED_INPUT = SCRIPT_DIR.parent / "outputs" / "all_drills_combined_unclassified.json"

# === LOAD FILES ===
with open(FULL_OUTPUT, "r") as f:
    ihs_weiss_classified = json.load(f)

with open(UNCLASSIFIED_INPUT, "r") as f:
    all_combined = json.load(f)

# === Extract Classified Hockey Canada Drills ===
hockey_canada_classified = [
    d for d in all_combined
    if d.get("source") == "Hockey Canada" and d.get("classified")
]

print(f"✅ Loaded {len(ihs_weiss_classified)} drills from IHS + Weiss")
print(f"✅ Found {len(hockey_canada_classified)} classified Hockey Canada drills")

# === Merge and Save
merged = hockey_canada_classified + ihs_weiss_classified
with open(UNIFIED_OUTPUT, "w") as f:
    json.dump(merged, f, indent=2)

print(f"\n📦 Saved merged classified drills: {len(merged)} total")
print(f"📁 File: {UNIFIED_OUTPUT}")
