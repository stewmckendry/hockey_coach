#!/usr/bin/env python3
"""Test multiple hockey scenarios for movement accuracy."""

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

def test_scenario(scenario, save_name):
    """Test a single scenario and show results."""
    
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
        
        # Quick validation
        validation = []
        
        # Check if starts from a player
        start_ok = False
        for p in players:
            dist = ((movement['from_pos']['x'] - p['coordinates']['x'])**2 + 
                   (movement['from_pos']['y'] - p['coordinates']['y'])**2)**0.5
            if dist < 5:
                validation.append(f"✅ Starts from {p.get('label', p['id'])}")
                start_ok = True
                break
        
        if not start_ok:
            validation.append(f"❌ Doesn't start from any player")
            all_good = False
        
        # Check pass targets
        if movement['type'] == 'pass':
            pass_ok = False
            for p in players:
                dist = ((movement['to_pos']['x'] - p['coordinates']['x'])**2 + 
                       (movement['to_pos']['y'] - p['coordinates']['y'])**2)**0.5
                if dist < 10:
                    validation.append(f"✅ Targets {p.get('label', p['id'])}")
                    pass_ok = True
                    break
            if not pass_ok:
                validation.append(f"❌ Doesn't target any player")
                all_good = False
        
        # Check shot targets
        if movement['type'] == 'shot':
            net_dist = abs(movement['to_pos']['x'] - 89)
            if net_dist < 5:
                validation.append(f"✅ Targets net")
            else:
                validation.append(f"❌ Misses net by {net_dist:.1f}")
                all_good = False
        
        for v in validation:
            print(f"  {v}")
    
    # Save spec
    output_file = Path(__file__).parent / "outputs" / f"{save_name}.json"
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(spec, f, indent=2)
    
    # Summary
    if all_good:
        print(f"\n✅ SUCCESS: All movements make hockey sense!")
    else:
        print(f"\n❌ ISSUES: Some movements don't make hockey sense")
    
    return all_good

def main():
    """Test multiple scenarios."""
    
    scenarios = [
        # Basic passing plays
        ("Defense to defense pass along the blue line", "d_to_d_pass"),
        
        # Shooting plays
        ("Left wing drives to net and shoots", "lw_drive_shoot"),
        
        # Rush plays
        ("2 on 1 rush - left wing passes to center who shoots", "2v1_rush"),
        
        # Cycle plays
        ("Forwards cycle the puck in the offensive zone", "cycle_play"),
        
        # Breakout plays
        ("Goalie passes to defenseman who breaks out to winger", "breakout_play")
    ]
    
    results = []
    
    print("="*80)
    print("TESTING MULTIPLE HOCKEY SCENARIOS")
    print("="*80)
    
    for scenario, save_name in scenarios:
        success = test_scenario(scenario, save_name)
        results.append((scenario, success))
        print("\n" + "-"*80)
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    success_count = sum(1 for _, success in results if success)
    print(f"\nResults: {success_count}/{len(results)} scenarios passed")
    
    for scenario, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {scenario}")
    
    if success_count == len(results):
        print("\n🎉 ALL SCENARIOS PASSED!")
    else:
        print(f"\n⚠️  {len(results) - success_count} scenarios need attention")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set in environment")
        sys.exit(1)
    
    main()