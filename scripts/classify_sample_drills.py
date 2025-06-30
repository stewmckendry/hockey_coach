import json
import os
import pandas as pd
from dotenv import load_dotenv
import openai
import time
from openai import OpenAI
from pathlib import Path

# === CONFIG ===
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_PATH = SCRIPT_DIR.parent / "source_data" / "source_data_drills_all.json"
JSON_OUT_PATH = SCRIPT_DIR.parent / "source_data" / "drills_classified_sample.json"
CSV_OUT_PATH = SCRIPT_DIR.parent / "source_data" / "drills_classified_sample.csv"
MODEL = "gpt-3.5-turbo"
SAMPLE_SIZE = 5
DELAY = 1.0  # polite pause between calls

# === LOAD OPENAI KEY ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env")

# === PROMPT TEMPLATE ===
def build_prompt(drill):
    return f"""
You are a youth hockey coach helping organize and classify drills.

Please classify the following drill with the following structured output:

- position: list of "Forward", "Defence", "Goalie"
- starting_zone: one of "Defensive Zone", "Neutral Zone", "Offensive Zone", or "All Zones"
- ending_zone: one of "Defensive Zone", "Neutral Zone", "Offensive Zone", or "All Zones"
- situation: list of terms like "Breakout", "Zone Entry", "Power Play", "Penalty Kill", "Faceoff", "Offensive Play", "Defensive Play", "Transition", "Small Area Game"
- hockey_skills: list of hockey skill tags like "Skating", "Passing", "Shooting", "Stickhandling", "Positioning", "Angling", "Gapping", "Forecheck", "Backcheck", "Shot Blocking", "Net Front Play", "Communication", "Timing"
- complexity: one of "Easy", "Intermediate", "Advanced" — think about what a 9–11 year old rep player could handle

Drill:
Title: {drill['title']}
Instructions: {drill.get('instructions', '')}
Teaching Points: {drill.get('teaching_points', '')}

Respond with JSON only, no explanation.
""".strip()

# === RUN CLASSIFICATION ===
def classify_drills(drills):
    results = []

    for i, drill in enumerate(drills):
        print(f"\n🔍 Classifying drill {i+1}/{len(drills)}: {drill['title']}")
        prompt = build_prompt(drill)

        try:
            client = OpenAI()  # auto-uses API key from env or config

            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )

            response_text = response.choices[0].message.content.strip()

            print("📥 Raw response:", response_text)

            parsed = json.loads(response_text)
            combined = {**drill, **parsed}
            results.append(combined)
            print("✅ Success")

        except Exception as e:
            print(f"❌ Error parsing drill '{drill['title']}': {e}")
            continue

        time.sleep(DELAY)

    return results

# === MAIN ===
def main():
    print("📥 Loading drills from:", INPUT_PATH)
    with open(INPUT_PATH, "r") as f:
        all_drills = json.load(f)

    sample = all_drills[:SAMPLE_SIZE]
    print(f"🧪 Running sample classification on {len(sample)} drills")

    results = classify_drills(sample)

    print("\n💾 Saving JSON:", JSON_OUT_PATH)
    with open(JSON_OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print("💾 Saving CSV:", CSV_OUT_PATH)
    df = pd.DataFrame(results)
    df.to_csv(CSV_OUT_PATH, index=False)

    print("✅ Done.")

if __name__ == "__main__":
    main()
