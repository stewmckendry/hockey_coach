#!/usr/bin/env python3
"""Debug movement mapping to see raw output."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'servers'))

from hockey_diagram_mcp_v3 import (
    analyze_hockey_query, 
    map_positions_with_llm,
    map_movements_with_llm
)

def main():
    """Debug movement mapping."""
    
    scenario = "Center at slot passes to right wing at net front who shoots on goal"
    
    print(f"Testing: {scenario}\n")
    
    # Analyze query
    analysis_result = analyze_hockey_query(scenario)
    
    if "error" in analysis_result:
        print(f"❌ Analysis failed: {analysis_result.get('error')}")
        return
    
    # Extract components
    components = analysis_result.get("components_with_assumptions", {})
    players_info = components.get("players", [])
    movements_info = components.get("movements", [])
    
    print("=" * 60)
    print("ANALYSIS RESULTS:")
    print("-" * 60)
    print(f"Players ({len(players_info)}):")
    for p in players_info:
        print(f"  - {p['id']}: {p['position_desc']}")
    
    print(f"\nMovements ({len(movements_info)}):")
    for m in movements_info:
        print(f"  - {m['id']}: {m['type']} from {m.get('from_player')} - {m['desc']}")
    
    # Map player positions
    print("\n" + "=" * 60)
    print("MAPPING PLAYER POSITIONS:")
    print("-" * 60)
    
    position_result = map_positions_with_llm(players_info, "offensive")
    
    if "players_mapped" in position_result:
        print(f"\nMapped {len(position_result['players_mapped'])} players:")
        for p in position_result["players_mapped"]:
            coords = p.get("coordinates", {})
            x = coords.get("x", p.get("x", 0))
            y = coords.get("y", p.get("y", 0))
            print(f"  - {p['id']} ({p.get('label')}): ({x:.1f}, {y:.1f})")
    
    # Create player spec for movement mapping
    players_spec = []
    for p in position_result.get("players_mapped", []):
        coords = p.get("coordinates", {})
        x = coords.get("x", p.get("x", 0))
        y = coords.get("y", p.get("y", 0))
        players_spec.append({
            "id": p["id"],
            "type": p.get("type", "forward"),
            "position": p["id"],
            "team": p.get("team", "home"),
            "coordinates": {"x": x, "y": y},
            "label": p.get("label", p["id"])
        })
    
    # Map movements
    print("\n" + "=" * 60)
    print("MAPPING MOVEMENTS:")
    print("-" * 60)
    
    # Prepare movements for mapping
    movements_for_mapping = []
    for idx, m in enumerate(movements_info):
        movements_for_mapping.append({
            "id": f"movement_{idx}",
            "desc": m["desc"],
            "type": m["type"],
            "from_player": m.get("from_player"),
            "to_area": m.get("to_area"),
            "original": m
        })
    
    movement_result = map_movements_with_llm(movements_for_mapping, players_spec, "offensive")
    
    print("\nRaw movement mapping result:")
    print(json.dumps(movement_result, indent=2))
    
    # Save debug output
    output_file = Path(__file__).parent / "outputs" / "debug_movement.json"
    output_file.parent.mkdir(exist_ok=True)
    
    debug_data = {
        "scenario": scenario,
        "analysis": analysis_result,
        "position_mapping": position_result,
        "players_spec": players_spec,
        "movement_mapping": movement_result
    }
    
    with open(output_file, 'w') as f:
        json.dump(debug_data, f, indent=2)
    
    print(f"\n📄 Debug data saved to: {output_file}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set in environment")
        sys.exit(1)
    
    main()