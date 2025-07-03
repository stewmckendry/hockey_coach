import json
import os
import pandas as pd
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# === CONFIG ===
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_PATH = SCRIPT_DIR.parent / "outputs" / "all_drills_combined_unclassified.json"
JSON_OUT_PATH = SCRIPT_DIR.parent / "outputs" / "drills_classified_full.json"
CSV_OUT_PATH = SCRIPT_DIR.parent / "outputs" / "drills_classified_full.csv"
MODEL = "gpt-3.5-turbo"
DELAY = 1.0

# === LOAD API KEY ===
load_dotenv()
client = OpenAI()

def build_prompt(drill):
    return f"""
You are a youth hockey coach helping organize and classify drills for a team of 9–11 year old players.

Please classify the following drill using ONLY the exact terms provided for each category:

- position: choose one or more from ["Forward", "Defence", "Goalie"]
    • Skating, passing, stickhandling drills → often involve Forwards and Defence
    • Shooting drills → often involve all 3 positions
    • Goalie-focused drills → include "Goalie"

- starting_zone: one of ["Defensive Zone", "Neutral Zone", "Offensive Zone", "All Zones", "Unknown"]
- ending_zone: one of the same values

- situation: choose zero or more from ["Breakout", "Zone Entry", "Power Play", "Penalty Kill", "Faceoff", "Offensive Play", "Defensive Play", "Transition", "Small Area Game"]
    • Net-front or down-low drills → "Small Area Game"
    • Puck retrieval, regroups, transitions → "Transition"
    • Pressuring defenders → "Forecheck" or "Defensive Play"
    • Zone movement or rushes → "Zone Entry"

Use only values from the lists above. If you're unsure, return an empty list [].

- hockey_skills: zero or more of ["Skating", "Passing", "Shooting", "Stickhandling", "Positioning", "Angling", "Gapping", "Forecheck", "Backcheck", "Shot Blocking", "Net Front Play", "Communication", "Timing"]

- complexity: one of ["Easy", "Intermediate", "Advanced"] — based on what a 9–11 year old rep player can handle

Drill:
Title: {drill['title']}
Instructions: {drill.get('instructions', '')}
Teaching Points: {drill.get('teaching_points', '')}
Summary: {drill.get('summary', '')}
Tags: {', '.join(drill.get('tags', []))}

Respond in valid JSON with keys: position, starting_zone, ending_zone, situation, hockey_skills, complexity.
""".strip()

# === LOAD INPUT ===
with open(INPUT_PATH, "r") as f:
    all_drills = json.load(f)

# === FILTER TO UNCLASSIFIED IHS & WEISS DRILLS ===
unclassified = [d for d in all_drills if d['source'] in {"IHS", "Weiss"} and not d.get("classified")]
print(f"🚀 Starting classification on {len(unclassified)} drills")

classified = []

# === MAIN LOOP ===
for i, drill in enumerate(unclassified):
    print(f"\n🔍 Classifying drill {i+1}/{len(unclassified)}: {drill['title']}")
    prompt = build_prompt(drill)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = response.choices[0].message.content.strip()
        print("📥 GPT Response:", content)

        parsed = json.loads(content)
        drill.update(parsed)
        drill["classified"] = True
        classified.append(drill)

    except (OpenAIError, json.JSONDecodeError) as e:
        print(f"❌ Error parsing drill '{drill['title']}': {e}")
        continue

    time.sleep(DELAY)

# === SAVE OUTPUT ===
with open(JSON_OUT_PATH, "w") as f:
    json.dump(classified, f, indent=2)
pd.DataFrame(classified).to_csv(CSV_OUT_PATH, index=False)

print(f"\n✅ Saved {len(classified)} classified drills to:")
print(f"  - JSON: {JSON_OUT_PATH}")
print(f"  - CSV:  {CSV_OUT_PATH}")
