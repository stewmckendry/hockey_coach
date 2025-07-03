import json
import pandas as pd
from pathlib import Path

# === Paths ===
SRC1 = Path("source_data/drills_classified_revised.json")      # Hockey Canada
SRC2 = Path("source_data/source2_drills_raw.json")             # IHS
SRC3 = Path("source_data/source3_drills_raw.json")             # Weiss

OUT_JSON = Path("outputs/all_drills_combined_unclassified.json")
OUT_CSV = Path("outputs/all_drills_combined_unclassified.csv")

def normalize_drill(raw, source):
    title = raw.get("title", "").strip()
    image_url = raw.get("image_url", "")
    video_url = raw.get("video_url", "")
    category = raw.get("category", None)
    author = raw.get("author", None)
    summary = None

    if source == "Hockey Canada":
        instructions = raw.get("instructions", "").strip()
        tp_raw = raw.get("teaching_points", [])
        if isinstance(tp_raw, str):
            teaching_points = [pt.strip() for pt in tp_raw.split(";") if pt.strip()]
        elif isinstance(tp_raw, list):
            teaching_points = tp_raw
        else:
            teaching_points = []
        return {
            "title": title,
            "image_url": image_url,
            "video_url": video_url,
            "source": source,
            "category": category,
            "author": author,
            "summary": summary,  # not provided by HC
            "instructions": instructions,
            "teaching_points": teaching_points,
            "variations": [],
            "tags": [],
            "classified": True,
            "position": raw.get("position", []),
            "starting_zone": raw.get("starting_zone", ""),
            "ending_zone": raw.get("ending_zone", ""),
            "situation": raw.get("situation", []),
            "hockey_skills": raw.get("hockey_skills", []),
            "complexity": raw.get("complexity", "")
        }

    elif source == "IHS":
        setup = raw.get("setup", "")
        if isinstance(setup, list):
            instructions = " ".join(setup).strip()
        else:
            instructions = str(setup).strip()

        coaching_points = raw.get("coaching_points", [])
        teaching_points = coaching_points if isinstance(coaching_points, list) else []

        summary = raw.get("summary", "")
        if isinstance(summary, list):
            summary = " ".join(summary).strip()
        else:
            summary = str(summary).strip()

        return {
            "title": title,
            "image_url": image_url,
            "video_url": video_url,
            "source": source,
            "category": category,
            "author": author,
            "summary": summary,
            "instructions": instructions,
            "teaching_points": teaching_points,
            "variations": raw.get("variations", []),
            "tags": raw.get("tags", []),
            "classified": False,
            "position": [],
            "starting_zone": "",
            "ending_zone": "",
            "situation": [],
            "hockey_skills": [],
            "complexity": ""
        }

    elif source == "Weiss":
        instructions = raw.get("instructions", "").strip()
        teaching_points = raw.get("teaching_points", [])
        return {
            "title": title,
            "image_url": image_url,
            "video_url": video_url,
            "source": source,
            "category": category,
            "author": author,
            "summary": summary,  # not provided by Weiss
            "instructions": instructions,
            "teaching_points": teaching_points if isinstance(teaching_points, list) else [],
            "variations": raw.get("variations", []),
            "tags": raw.get("tags", []),
            "classified": False,
            "position": [],
            "starting_zone": "",
            "ending_zone": "",
            "situation": [],
            "hockey_skills": [],
            "complexity": ""
        }

    else:
        raise ValueError(f"Unknown source: {source}")

def load_and_normalize(path: Path, source_name: str):
    with open(path, "r") as f:
        drills = json.load(f)
    print(f"✅ Loaded {len(drills)} drills from {source_name}")
    return [normalize_drill(d, source_name) for d in drills]

def main():
    all_drills = []
    all_drills += load_and_normalize(SRC1, "Hockey Canada")
    all_drills += load_and_normalize(SRC2, "IHS")
    all_drills += load_and_normalize(SRC3, "Weiss")

    print(f"\n🔢 Total combined drills: {len(all_drills)}")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(all_drills, f, indent=2)
    print(f"💾 Saved JSON to: {OUT_JSON}")

    df = pd.DataFrame(all_drills)
    df.to_csv(OUT_CSV, index=False)
    print(f"💾 Saved CSV to: {OUT_CSV}")

if __name__ == "__main__":
    main()
