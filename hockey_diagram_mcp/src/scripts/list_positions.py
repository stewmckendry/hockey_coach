#!/usr/bin/env python3
"""
List all standard hockey positions defined in position_mapper.py
For easy validation and editing.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "servers"))

from position_mapper import OFFENSIVE_POSITIONS, DEFENSIVE_POSITIONS, NEUTRAL_POSITIONS

def print_positions():
    print("=" * 80)
    print("HOCKEY POSITION MAPPINGS")
    print("=" * 80)
    
    print("\n🔴 OFFENSIVE ZONE POSITIONS (attacking towards x=-100)")
    print("-" * 50)
    for name, (x, y) in sorted(OFFENSIVE_POSITIONS.items()):
        print(f"  {name:<35} ({x:>6.1f}, {y:>6.1f})")
    
    print(f"\n  Total: {len(OFFENSIVE_POSITIONS)} positions")
    
    print("\n🔵 DEFENSIVE ZONE POSITIONS (defending x=+100)")
    print("-" * 50)
    for name, (x, y) in sorted(DEFENSIVE_POSITIONS.items()):
        print(f"  {name:<35} ({x:>6.1f}, {y:>6.1f})")
    
    print(f"\n  Total: {len(DEFENSIVE_POSITIONS)} positions")
    
    print("\n⚪ NEUTRAL ZONE POSITIONS (center ice)")
    print("-" * 50)
    for name, (x, y) in sorted(NEUTRAL_POSITIONS.items()):
        print(f"  {name:<35} ({x:>6.1f}, {y:>6.1f})")
    
    print(f"\n  Total: {len(NEUTRAL_POSITIONS)} positions")
    
    print("\n" + "=" * 80)
    print(f"GRAND TOTAL: {len(OFFENSIVE_POSITIONS) + len(DEFENSIVE_POSITIONS) + len(NEUTRAL_POSITIONS)} positions defined")
    print("=" * 80)
    
    # Quick validation check
    print("\n🔍 VALIDATION CHECKS:")
    print("-" * 50)
    
    # Check for duplicates within zones
    all_positions = [
        ("Offensive", OFFENSIVE_POSITIONS),
        ("Defensive", DEFENSIVE_POSITIONS),
        ("Neutral", NEUTRAL_POSITIONS)
    ]
    
    issues = []
    for zone_name, positions in all_positions:
        coords_to_names = {}
        for name, coords in positions.items():
            coord_str = f"{coords}"
            if coord_str in coords_to_names:
                issues.append(f"  ⚠️  {zone_name}: '{name}' and '{coords_to_names[coord_str]}' have same coords {coords}")
            else:
                coords_to_names[coord_str] = name
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(issue)
    else:
        print("  ✅ No duplicate coordinates within zones")
    
    # Check coordinate ranges
    out_of_bounds = []
    for zone_name, positions in all_positions:
        for name, (x, y) in positions.items():
            if not (-100 <= x <= 100):
                out_of_bounds.append(f"  ⚠️  {zone_name}: '{name}' x={x} out of bounds [-100, 100]")
            if not (-42.5 <= y <= 42.5):
                out_of_bounds.append(f"  ⚠️  {zone_name}: '{name}' y={y} out of bounds [-42.5, 42.5]")
    
    if out_of_bounds:
        print("\nOut of bounds positions:")
        for oob in out_of_bounds:
            print(oob)
    else:
        print("  ✅ All coordinates within valid rink bounds")

if __name__ == "__main__":
    print_positions()