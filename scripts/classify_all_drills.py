import json
import os
import pandas as pd
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# === CONFIG ===
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_PATH = SCRIPT_DIR.parent / "hockey_canada" / "hockey_canada_drills_all.json"
JSON_OUT_PATH = SCRIPT_DIR.parent / "hockey_canada" / "drills_classified_full.json"
CSV_OUT_PATH = SCRIPT_DIR.parent / "hockey_canada" / "drills_classified_full.csv"
MODEL = "gpt-3.5-turbo"
DELAY = 1.0  # seconds between calls

# === LOAD API KEY ===
load_dotenv()
client = OpenAI()

# === PROMPT BUILDER ===
def build_prompt(drill):
    return f"""
You are a youth hockey coach helping organize and classify drills for a team of 9–11 year old players.

Please classify the following drill using ONLY the exact terms provided for each category:

- position: one or more of ["Forward", "Defence", "Goalie"]
- starting_zone: one of ["Defensive Zone", "Neutral Zone", "Offensive Zone", "All Zones", "Unknown"]
- ending_zone: same as starting_zone values
- situation: zero or more of ["Breakout", "Zone Entry", "Power Play", "Penalty Kill", "Faceoff", "Offensive Play", "Defensive Play", "Transition", "Small Area Game"]
- hockey_skills: zero or more of ["Skating", "Passing", "Shooting", "Stickhandling", "Positioning", "Angling", "Gapping", "Forecheck", "Backcheck", "Shot Blocking", "Net Front Play", "Communication", "Timing"]
- complexity: one of ["Easy", "Intermediate", "Advanced"] — based on what a 9–11 year old rep player can handle

If the drill spans multiple zones or is unclear, use "All Zones" or "Unknown" for zone fields.
If unsure about a category, leave the list empty.

Drill:
Title: {drill['title']}
Instructions: {drill.get('instructions', '')}
Teaching Points: {drill.get('teaching_points', '')}

Respond with JSON only, no explanation.
""".strip()

# === LOAD DRILLS ===
with open(INPUT_PATH, "r") as f:
    all_drills = json.load(f)

# === RESUME SUPPORT ===
if os.path.exists(JSON_OUT_PATH):
    with open(JSON_OUT_PATH, "r") as f:
        classified = json.load(f)
    processed_titles = {d['title'] for d in classified}
    print(f"🔁 Resuming from {len(classified)} classified drills")
else:
    classified = []
    processed_titles = set()

# === MAIN LOOP ===
for i, drill in enumerate(all_drills):
    if drill['title'] in processed_titles:
        continue

    print(f"\n🔍 Classifying {len(classified)+1}/{len(all_drills)}: {drill['title']}")

    prompt = build_prompt(drill)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = response.choices[0].message.content.strip()
        print("📥 Response:", content)

        parsed = json.loads(content)
        combined = {**drill, **parsed}
        classified.append(combined)
        processed_titles.add(drill['title'])
        print("✅ Classification added")

        # Save after each drill
        with open(JSON_OUT_PATH, "w") as f:
            json.dump(classified, f, indent=2)

        df = pd.DataFrame(classified)
        df.to_csv(CSV_OUT_PATH, index=False)

    except (OpenAIError, json.JSONDecodeError) as e:
        print(f"❌ Error on drill {drill['title']}: {e}")
        print("⏳ Waiting before retry...")
        time.sleep(5)
        continue

    time.sleep(DELAY)

print("\n🏁 All drills classified and saved.")
