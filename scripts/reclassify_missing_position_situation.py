import json
import os
import time
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# === CONFIG ===
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_PATH = SCRIPT_DIR.parent / "source_data" / "drills_classified_full.json"
JSON_OUT_PATH = SCRIPT_DIR.parent / "source_data" / "drills_classified_revised.json"
CSV_OUT_PATH = SCRIPT_DIR.parent / "source_data" / "drills_classified_revised.csv"
MODEL = "gpt-3.5-turbo"
DELAY = 1.0  # seconds between calls

# === LOAD API KEY ===
load_dotenv()
client = OpenAI()

# === PROMPT BUILDER ===
def build_prompt(drill):
    return f"""
You are a youth hockey coach helping organize drills for 9–11 year old players.

This drill is missing `position` and/or `situation` classifications. Please infer them based on the title, instructions, and teaching points.

Guidelines:

- position: choose one or more from ["Forward", "Defence", "Goalie"]
    • Skating, passing, stickhandling drills → often involve Forwards and Defence
    • Shooting drills → often involve all 3 positions
    • Goalie-focused drills → include "Goalie"

- situation: choose zero or more from ["Breakout", "Zone Entry", "Power Play", "Penalty Kill", "Faceoff", "Offensive Play", "Defensive Play", "Transition", "Small Area Game"]
    • Net-front or down-low drills → "Small Area Game"
    • Puck retrieval, regroups, transitions → "Transition"
    • Pressuring defenders → "Forecheck" or "Defensive Play"
    • Zone movement or rushes → "Zone Entry"

Use only values from the lists above. If you’re unsure, return empty list [].

Return JSON like:
{{"position": [...], "situation": [...]}}

Drill:
Title: {drill['title']}
Instructions: {drill.get('instructions', '')}
Teaching Points: {drill.get('teaching_points', '')}
""".strip()

# === LOAD EXISTING CLASSIFIED DATA ===
with open(INPUT_PATH, "r") as f:
    all_drills = json.load(f)

print(f"📥 Loaded {len(all_drills)} drills")

# === FILTER TO ONLY INCOMPLETE ===
to_update = [d for d in all_drills if not d.get("position") or not d.get("situation")]
print(f"🔍 {len(to_update)} drills need reclassification (missing position or situation)\n")

# === MAIN LOOP ===
updated = []
for i, drill in enumerate(to_update):
    print(f"🔄 {i+1}/{len(to_update)}: {drill['title']}")

    prompt = build_prompt(drill)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = response.choices[0].message.content.strip()
        print("📥 GPT response:", content)
        parsed = json.loads(content)

        drill['position'] = parsed.get("position", [])
        drill['situation'] = parsed.get("situation", [])
        updated.append(drill)
        print("✅ Updated\n")

    except (OpenAIError, json.JSONDecodeError) as e:
        print(f"❌ Error: {e}")
        time.sleep(5)
        continue

    time.sleep(DELAY)

# === MERGE UPDATES ===
updated_titles = {d["title"] for d in updated}
merged = [
    d if d["title"] not in updated_titles else next(u for u in updated if u["title"] == d["title"])
    for d in all_drills
]

# === SAVE OUTPUT ===
print(f"\n💾 Saving updated dataset: {len(merged)} drills")
with open(JSON_OUT_PATH, "w") as f:
    json.dump(merged, f, indent=2)

pd.DataFrame(merged).to_csv(CSV_OUT_PATH, index=False)
print("✅ All done.")
