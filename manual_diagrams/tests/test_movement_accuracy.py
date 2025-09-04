#!/usr/bin/env python3
"""Test movement coordinate accuracy and hockey sense validation."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'servers'))

from hockey_diagram_mcp_v3 import (
    analyze_hockey_query, 
    translate_analysis_to_spec
)

def analyze_movement_accuracy(spec, query):
    """Analyze if movements make hockey sense based on the query."""
    
    print(f"\n{'='*80}")
    print(f"MOVEMENT ACCURACY ANALYSIS")
    print(f"{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    # Extract players and movements
    players = spec.get("players", [])
    movements = spec.get("movements", [])
    
    # Create player position map
    player_map = {}
    for player in players:
        player_map[player["id"]] = {
            "position": player.get("label", player["id"]),
            "coords": player["coordinates"],
            "team": player["team"],
            "type": player["type"]
        }
    
    print("PLAYER POSITIONS:")
    print("-" * 40)
    for pid, info in player_map.items():
        print(f"{info['position']:5} ({info['team']:4}): ({info['coords']['x']:6.1f}, {info['coords']['y']:6.1f}) - {info['type']}")
    
    print(f"\n{'='*40}")
    print("MOVEMENT ANALYSIS:")
    print("-" * 40)
    
    for idx, movement in enumerate(movements, 1):
        print(f"\nMovement {idx}: {movement['type'].upper()}")
        print(f"  From: ({movement['from_pos']['x']:6.1f}, {movement['from_pos']['y']:6.1f})")
        print(f"  To:   ({movement['to_pos']['x']:6.1f}, {movement['to_pos']['y']:6.1f})")
        
        # Calculate distance
        dx = movement['to_pos']['x'] - movement['from_pos']['x']
        dy = movement['to_pos']['y'] - movement['from_pos']['y']
        distance = (dx**2 + dy**2)**0.5
        print(f"  Distance: {distance:.1f} units")
        
        # Check waypoints
        waypoints = movement.get('waypoints', [])
        if waypoints:
            print(f"  Waypoints: {len(waypoints)}")
            for wp in waypoints:
                print(f"    - ({wp['x']:6.1f}, {wp['y']:6.1f})")
        
        # Hockey sense checks
        print(f"  Hockey Sense Checks:")
        
        # Check if pass/shot is toward offensive zone
        if movement['type'] in ['pass', 'shot']:
            if dx > 0:  # Moving toward offensive net (x=89)
                print(f"    ✅ Moving toward offensive zone (good)")
            else:
                print(f"    ⚠️  Moving away from offensive zone (check intent)")
        
        # Check if shot ends near net
        if movement['type'] == 'shot':
            net_x = 89
            to_net_dist = abs(movement['to_pos']['x'] - net_x)
            if to_net_dist < 5:
                print(f"    ✅ Shot targets net area (distance: {to_net_dist:.1f})")
            else:
                print(f"    ❌ Shot doesn't target net (distance: {to_net_dist:.1f})")
        
        # Check if movement starts/ends near a player
        start_near_player = None
        end_near_player = None
        
        for pid, info in player_map.items():
            # Check start position
            start_dist = ((movement['from_pos']['x'] - info['coords']['x'])**2 + 
                         (movement['from_pos']['y'] - info['coords']['y'])**2)**0.5
            if start_dist < 5:
                start_near_player = info['position']
            
            # Check end position
            end_dist = ((movement['to_pos']['x'] - info['coords']['x'])**2 + 
                       (movement['to_pos']['y'] - info['coords']['y'])**2)**0.5
            if end_dist < 5:
                end_near_player = info['position']
        
        if start_near_player:
            print(f"    ✅ Starts near {start_near_player}")
        else:
            print(f"    ⚠️  Doesn't start near any player")
            
        if movement['type'] == 'pass' and end_near_player:
            print(f"    ✅ Pass targets {end_near_player}")
        elif movement['type'] == 'pass':
            print(f"    ⚠️  Pass doesn't clearly target a player")

def test_scenarios():
    """Test multiple hockey scenarios."""
    
    scenarios = [
        "Center at slot passes to right wing at net front who shoots on goal",
        "Defense to defense pass along the blue line then shot from point",
        "Breakout pass from goalie to left wing who carries into offensive zone",
        "3v2 drill - forwards cycle the puck around the offensive zone",
        "Faceoff win back to defense who takes a slap shot"
    ]
    
    for scenario in scenarios:
        print("\n" + "="*80)
        print(f"SCENARIO: {scenario}")
        print("="*80)
        
        # Analyze query
        analysis_result = analyze_hockey_query(scenario)
        
        if "error" in analysis_result:
            print(f"❌ Analysis failed: {analysis_result.get('error')}")
            continue
        
        # Translate to spec
        translate_result = translate_analysis_to_spec(
            analysis_result,
            title=scenario[:50]
        )
        
        if not translate_result.get("success"):
            print(f"❌ Translation failed: {translate_result.get('error')}")
            continue
        
        spec = translate_result["spec"]
        
        # Analyze movement accuracy
        analyze_movement_accuracy(spec, scenario)
        
        # Save spec for inspection
        output_file = Path(__file__).parent / "outputs" / f"movement_test_{scenarios.index(scenario)}.json"
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(spec, f, indent=2)
        print(f"\n📄 Spec saved to: {output_file}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set in environment")
        sys.exit(1)
    
    test_scenarios()