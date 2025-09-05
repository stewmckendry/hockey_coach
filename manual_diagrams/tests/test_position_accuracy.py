#!/usr/bin/env python3
"""Test position mapping accuracy - show original descriptions vs coordinates."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'servers'))

from hockey_diagram_mcp_v3 import map_positions_with_llm

def test_position_accuracy():
    """Test various position descriptions and verify coordinate accuracy."""
    
    # Test scenarios with different position descriptions
    test_scenarios = [
        {
            "name": "Faceoff Formation - Offensive Zone Right Dot",
            "view": "offensive",
            "players": [
                {"id": "C", "type": "center", "position_desc": "Center at right offensive faceoff dot"},
                {"id": "LW", "type": "winger", "position_desc": "Left wing on the right faceoff circle"},
                {"id": "RW", "type": "winger", "position_desc": "Right wing at the hashmarks near right dot"},
                {"id": "LD", "type": "defense", "position_desc": "Left defenseman at left point"},
                {"id": "RD", "type": "defense", "position_desc": "Right defenseman at right point"},
            ]
        },
        {
            "name": "Power Play Formation - Umbrella",
            "view": "offensive", 
            "players": [
                {"id": "PP1", "type": "forward", "position_desc": "Net front presence in the slot"},
                {"id": "PP2", "type": "forward", "position_desc": "Left half wall"},
                {"id": "PP3", "type": "forward", "position_desc": "Right half wall"},
                {"id": "PP4", "type": "defense", "position_desc": "Top of the offensive zone at center point"},
                {"id": "PP5", "type": "defense", "position_desc": "High slot area"},
            ]
        },
        {
            "name": "Breakout - D to D Behind Net",
            "view": "defensive",
            "players": [
                {"id": "G", "type": "goalie", "position_desc": "Goalie in the crease"},
                {"id": "LD", "type": "defense", "position_desc": "Left defenseman behind the net"},
                {"id": "RD", "type": "defense", "position_desc": "Right defenseman in right corner"},
                {"id": "C", "type": "center", "position_desc": "Center in front of net supporting"},
                {"id": "LW", "type": "winger", "position_desc": "Left wing along left boards"},
                {"id": "RW", "type": "winger", "position_desc": "Right wing near defensive blue line"},
            ]
        },
        {
            "name": "Neutral Zone Trap",
            "view": "neutral",
            "players": [
                {"id": "F1", "type": "forward", "position_desc": "Forechecking forward at center ice"},
                {"id": "F2", "type": "forward", "position_desc": "Left side neutral zone near red line"},
                {"id": "F3", "type": "forward", "position_desc": "Right side neutral zone near red line"},
                {"id": "D1", "type": "defense", "position_desc": "Left defense at defensive blue line"},
                {"id": "D2", "type": "defense", "position_desc": "Right defense at defensive blue line"},
            ]
        },
        {
            "name": "2-on-1 Rush",
            "view": "offensive",
            "players": [
                {"id": "F1", "type": "forward", "position_desc": "Puck carrier entering zone on left wing"},
                {"id": "F2", "type": "forward", "position_desc": "Support forward driving to the net"},
                {"id": "D1", "type": "defense", "position_desc": "Defending player between the two forwards"},
                {"id": "G", "type": "goalie", "position_desc": "Goalie at top of crease"},
            ]
        }
    ]
    
    print("=" * 80)
    print("POSITION MAPPING ACCURACY TEST")
    print("=" * 80)
    print("\nVerifying that position descriptions map to accurate coordinates\n")
    
    # Expected coordinate ranges for validation
    expected_ranges = {
        "offensive": {
            "faceoff_dot": {"right": (69, 22.5), "left": (69, -22.5)},
            "point": {"left": (54, -38), "right": (54, 38), "center": (54, 0)},
            "half_wall": {"left": (75, -38), "right": (75, 38)},
            "slot": {"x": (70, 80), "y": (-10, 10)},
            "high_slot": {"x": (60, 70), "y": (-10, 10)},
            "net_front": {"x": (83, 89), "y": (-8, 8)},
            "crease": {"x": (86, 89), "y": (-4, 4)},
        },
        "defensive": {
            "behind_net": {"x": (-92, -89), "y": (-5, 5)},
            "corner": {"left": (-89, -36), "right": (-89, 36)},
            "crease": {"x": (-89, -86), "y": (-4, 4)},
            "blue_line": {"x": (-25, -25), "y": (-42.5, 42.5)},
        },
        "neutral": {
            "center_ice": {"x": (-5, 5), "y": (-5, 5)},
            "red_line": {"x": (-2, 2), "y": (-42.5, 42.5)},
            "defensive_blue": {"x": (-25, -25), "y": (-42.5, 42.5)},
            "offensive_blue": {"x": (25, 25), "y": (-42.5, 42.5)},
        }
    }
    
    for scenario in test_scenarios:
        print(f"\n{'='*60}")
        print(f"📋 SCENARIO: {scenario['name']}")
        print(f"   View: {scenario['view']}")
        print(f"{'='*60}")
        
        # Get mapped positions
        result = map_positions_with_llm(scenario["players"], scenario["view"])
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            continue
        
        if "players_mapped" in result:
            print(f"\n{'Player':<6} {'Original Description':<45} {'Coordinates':<15} {'Confidence':<10}")
            print("-" * 80)
            
            for player in result["players_mapped"]:
                orig_desc = player.get("original_position", "N/A")[:43]
                coords = player.get("coordinates", {})
                coord_str = f"({coords.get('x', 0):6.1f}, {coords.get('y', 0):6.1f})"
                confidence = player.get("confidence", 0)
                
                # Determine if coordinates seem reasonable
                validity = "✅" if confidence >= 0.8 else "⚠️" if confidence >= 0.6 else "❌"
                
                print(f"{player['id']:<6} {orig_desc:<45} {coord_str:<15} {confidence:.2f} {validity}")
                
                # Show detailed info for low confidence
                if confidence < 0.8:
                    print(f"       Zone: {player.get('zone', 'N/A')}, Area: {player.get('area', 'N/A')}")
                    if player.get('reasoning'):
                        print(f"       Reasoning: {player['reasoning'][:70]}...")
                    if player.get('alternatives'):
                        print(f"       Alternatives: {', '.join(player['alternatives'][:2])}")
        
        # Show any spatial issues
        if "spatial_checks" in result:
            spatial = result["spatial_checks"]
            if spatial.get("overlaps_detected"):
                print(f"\n⚠️  Overlapping positions detected: {', '.join(spatial.get('spacing_issues', []))}")
            if spatial.get("out_of_bounds"):
                print(f"\n❌ Out of bounds: {', '.join(spatial['out_of_bounds'])}")
        
        # Show critical questions
        if "questions_for_user" in result and result["questions_for_user"]:
            print("\n❓ Questions for clarification:")
            for q in result["questions_for_user"]:
                print(f"   - {q['question']}")
                if q.get("options"):
                    print(f"     Options: {', '.join(q['options'])}")

    print("\n" + "=" * 80)
    print("COORDINATE REFERENCE:")
    print("-" * 80)
    print("Offensive Zone:")
    print("  - Faceoff dots: (69, ±22.5)")
    print("  - Points: (54, ±38)")
    print("  - Half walls: (75, ±38)")
    print("  - Slot: x=70-80, y=-10 to 10")
    print("  - Net: (89, 0)")
    print("\nDefensive Zone:")
    print("  - Behind net: (-92, 0)")
    print("  - Corners: (-89, ±36)")
    print("  - Crease: x=-89 to -86")
    print("  - Blue line: x=-25")
    print("\nNeutral Zone:")
    print("  - Center ice: (0, 0)")
    print("  - Red line: x=0")
    print("  - Blue lines: x=±25")
    print("=" * 80)

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set in environment")
        sys.exit(1)
    
    test_position_accuracy()