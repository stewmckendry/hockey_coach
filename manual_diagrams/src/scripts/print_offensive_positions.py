#!/usr/bin/env python3
"""
Print list of offensive zone positions with coordinates.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "servers"))

from position_mapper import OFFENSIVE_POSITIONS

print("\n" + "="*80)
print("                    OFFENSIVE ZONE POSITIONS")
print("="*80)
print("\nCoordinate System: x: -100 to 100 (left to right), y: -42.5 to 42.5 (bottom to top)")
print("Offensive zone: LEFT side of rink (negative x values)")
print("Home team attacks this zone\n")

# Group positions by category
categories = {
    "FACEOFF DOTS": [],
    "FACEOFF POSITIONS - HOME TEAM": [],
    "FACEOFF POSITIONS - AWAY TEAM": [],
    "NET AREA": [],
    "SLOT AREA": [],
    "HASH MARKS": [],
    "CORNERS": [],
    "HALF WALL": [],
    "BLUE LINE/POINTS": [],
    "GOAL LINE": [],
    "QUEUE POSITIONS": []
}

for name, coords in sorted(OFFENSIVE_POSITIONS.items()):
    if "faceoff home" in name:
        categories["FACEOFF POSITIONS - HOME TEAM"].append((name, coords))
    elif "faceoff away" in name:
        categories["FACEOFF POSITIONS - AWAY TEAM"].append((name, coords))
    elif "faceoff dot" in name or "dot" in name:
        categories["FACEOFF DOTS"].append((name, coords))
    elif any(x in name for x in ["net", "crease", "post"]):
        categories["NET AREA"].append((name, coords))
    elif "slot" in name:
        categories["SLOT AREA"].append((name, coords))
    elif "hash" in name:
        categories["HASH MARKS"].append((name, coords))
    elif "corner" in name:
        categories["CORNERS"].append((name, coords))
    elif "half wall" in name or "wall" in name:
        categories["HALF WALL"].append((name, coords))
    elif any(x in name for x in ["point", "blue line"]):
        categories["BLUE LINE/POINTS"].append((name, coords))
    elif "goal line" in name:
        categories["GOAL LINE"].append((name, coords))
    elif "queue" in name:
        categories["QUEUE POSITIONS"].append((name, coords))

# Print by category
for category, positions in categories.items():
    if positions:
        print(f"\n{category}")
        print("-" * len(category))
        for name, (x, y) in positions:
            print(f"{name:<45} ({x:>6.1f}, {y:>6.1f})")

print(f"\n\nTOTAL OFFENSIVE ZONE POSITIONS: {len(OFFENSIVE_POSITIONS)}")
print("="*80)