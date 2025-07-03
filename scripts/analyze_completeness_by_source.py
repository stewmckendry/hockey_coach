import json
from collections import defaultdict
from pathlib import Path
from rich import print
from rich.table import Table
from pathlib import Path

# Path to normalized merged drill file
SCRIPT_DIR = Path(__file__).resolve().parent
MERGED_PATH = SCRIPT_DIR.parent / "outputs" / "all_drills_combined_unclassified.json"

def analyze_completeness(drills):
    sources = defaultdict(list)
    for d in drills:
        sources[d["source"]].append(d)

    fields_to_check = [
        "title", "image_url", "video_url", "category", "author", "summary",
        "instructions", "teaching_points", "variations", "tags",
        "classified", "position", "starting_zone", "ending_zone",
        "situation", "hockey_skills", "complexity"
    ]

    for source, drills in sources.items():
        print(f"\n📊 [bold cyan]Source: {source}[/bold cyan] — {len(drills)} drills")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Field")
        table.add_column("Non-empty", justify="right")
        table.add_column("Empty", justify="right")

        for field in fields_to_check:
            non_empty = sum(
                bool(d.get(field)) and (len(d.get(field)) if isinstance(d.get(field), (list, str)) else True)
                for d in drills
            )
            empty = len(drills) - non_empty
            table.add_row(field, str(non_empty), str(empty))

        print(table)

def main():
    print(f"📥 Loading merged drills from: {MERGED_PATH}")
    with open(MERGED_PATH, "r") as f:
        drills = json.load(f)

    analyze_completeness(drills)

if __name__ == "__main__":
    main()
