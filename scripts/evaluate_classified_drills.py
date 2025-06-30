import json
import os
from pathlib import Path
from collections import Counter
import pandas as pd

# === CONFIG ===
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_PATH = SCRIPT_DIR.parent / "source_data" / "drills_classified_full.json"

# === EXPECTED VALUES ===
EXPECTED = {
    "position": {"Forward", "Defence", "Goalie"},
    "starting_zone": {"Defensive Zone", "Neutral Zone", "Offensive Zone", "All Zones", "Unknown"},
    "ending_zone": {"Defensive Zone", "Neutral Zone", "Offensive Zone", "All Zones", "Unknown"},
    "situation": {
        "Breakout", "Zone Entry", "Power Play", "Penalty Kill", "Faceoff",
        "Offensive Play", "Defensive Play", "Transition", "Small Area Game"
    },
    "hockey_skills": {
        "Skating", "Passing", "Shooting", "Stickhandling", "Positioning",
        "Angling", "Gapping", "Forecheck", "Backcheck",
        "Shot Blocking", "Net Front Play", "Communication", "Timing"
    },
    "complexity": {"Easy", "Intermediate", "Advanced"}
}

# === LOAD DRILLS ===
with open(INPUT_PATH, "r") as f:
    drills = json.load(f)

print(f"📥 Loaded {len(drills)} drills\n")

# === EVALUATION ===
def evaluate_field(field_name, is_list=False):
    print(f"🔎 {field_name}")
    values = []
    missing = 0
    for d in drills:
        val = d.get(field_name)
        if not val or (is_list and len(val) == 0):
            missing += 1
        else:
            if is_list:
                values.extend(val)
            else:
                values.append(val)

    present_count = len(drills) - missing
    print(f"  ✓ Non-empty: {present_count} drills ({present_count / len(drills) * 100:.1f}%)")

    counter = Counter(values)
    for value, count in counter.most_common():
        print(f"  • {value}: {count}")

    # Check for unexpected values
    expected = EXPECTED[field_name]
    unexpected = [v for v in counter if v not in expected]
    if unexpected:
        print(f"  ⚠️ Unexpected values: {unexpected}")
    print()

# === RUN ANALYSIS ===
evaluate_field("position", is_list=True)
evaluate_field("starting_zone")
evaluate_field("ending_zone")
evaluate_field("situation", is_list=True)
evaluate_field("hockey_skills", is_list=True)
evaluate_field("complexity")
