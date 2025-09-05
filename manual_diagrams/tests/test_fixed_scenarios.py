#!/usr/bin/env python3
"""Test the problematic scenarios after fix."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'servers'))

from hockey_diagram_mcp_v3 import (
    analyze_hockey_query, 
    translate_analysis_to_spec
)

def test_scenario(scenario, name):
    """Test a single scenario."""
    
    print(f"\n{'='*80}")
    print(f"TESTING: {scenario}")
    print(f"{'='*80}")
    
    # Analyze query
    analysis_result = analyze_hockey_query(scenario)
    
    if "error" in analysis_result:
        print(f"❌ Analysis failed: {analysis_result.get('error')}")
        return False
    
    # Translate to spec
    translate_result = translate_analysis_to_spec(
        analysis_result,
        title=scenario[:50]
    )
    
    if not translate_result.get("success"):
        print(f"❌ Translation failed: {translate_result.get('error')}")
        return False
    
    spec = translate_result["spec"]
    
    # Extract players and movements
    players = spec.get("players", [])
    movements = spec.get("movements", [])
    
    # Show player positions
    print("\nPLAYER POSITIONS:")
    print("-" * 40)
    for player in players:
        coords = player["coordinates"]
        print(f"{player.get('label', player['id']):5} ({player['team']:4}): ({coords['x']:6.1f}, {coords['y']:6.1f})")
    
    # Show movements
    print("\nMOVEMENTS:")
    print("-" * 40)
    
    all_good = True
    for idx, movement in enumerate(movements, 1):
        print(f"\nMovement {idx}: {movement['type'].upper()}")
        print(f"  From: ({movement['from_pos']['x']:6.1f}, {movement['from_pos']['y']:6.1f})")
        print(f"  To:   ({movement['to_pos']['x']:6.1f}, {movement['to_pos']['y']:6.1f})")
        
        # Calculate distance
        dx = movement['to_pos']['x'] - movement['from_pos']['x']
        dy = movement['to_pos']['y'] - movement['from_pos']['y']
        distance = (dx**2 + dy**2)**0.5
        print(f"  Distance: {distance:.1f} units")
        
        # Check if starts from a player
        start_ok = False
        for p in players:
            dist = ((movement['from_pos']['x'] - p['coordinates']['x'])**2 + 
                   (movement['from_pos']['y'] - p['coordinates']['y'])**2)**0.5
            if dist < 5:
                print(f"  ✅ Starts from {p.get('label', p['id'])}")
                start_ok = True
                break
        
        if not start_ok:
            print(f"  ❌ Doesn't start from any player")
            all_good = False
        
        # Check pass targets
        if movement['type'] == 'pass':
            pass_ok = False
            for p in players:
                dist = ((movement['to_pos']['x'] - p['coordinates']['x'])**2 + 
                       (movement['to_pos']['y'] - p['coordinates']['y'])**2)**0.5
                if dist < 10:
                    print(f"  ✅ Targets {p.get('label', p['id'])} (dist: {dist:.1f})")
                    pass_ok = True
                    break
            if not pass_ok:
                print(f"  ❌ Doesn't target any player")
                all_good = False
    
    # Save spec
    output_file = Path(__file__).parent / "outputs" / f"fixed_{name}.json"
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(spec, f, indent=2)
    
    # Summary
    if all_good:
        print(f"\n✅ SUCCESS: All movements make hockey sense!")
    else:
        print(f"\n❌ ISSUES: Some movements still don't make hockey sense")
    
    return all_good

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test the previously problematic scenarios
    scenarios = [
        ("Forwards cycle the puck in the offensive zone", "cycle"),
        ("Goalie passes to defenseman who breaks out to winger", "breakout")
    ]
    
    print("="*80)
    print("TESTING FIXED SCENARIOS")
    print("="*80)
    
    results = []
    for scenario, name in scenarios:
        success = test_scenario(scenario, name)
        results.append((scenario, success))
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for scenario, success in results:
        status = "✅ FIXED" if success else "❌ STILL BROKEN"
        print(f"{status}: {scenario}")