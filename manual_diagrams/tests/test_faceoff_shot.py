#!/usr/bin/env python3
"""Test offensive zone faceoff with win-back and shot."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from servers.hockey_diagram_mcp_v3 import analyze_hockey_query, translate_analysis_to_spec, generate_diagram

def test_faceoff_shot():
    """Test offensive zone faceoff scenario with movements."""
    
    print("=" * 80)
    print("Testing: Offensive Zone Faceoff → Win Back → Defense Shot")
    print("=" * 80)
    
    # Step 1: Analyze the query (without using Exa MCP for now)
    query = "offensive zone faceoff at right dot, center wins puck back to left defenseman at left point, defenseman takes slap shot on goal"
    
    print("\n1. Analyzing query...")
    print(f"   Query: {query}")
    
    # For now, manually create the analysis to bypass the MCP issue
    analysis = {
        "original_query": query,
        "explicit_info": {
            "situation": "faceoff",
            "zone": "offensive",
            "key_actions": ["faceoff win", "pass back to defense", "shot on goal"],
            "faceoff_location": "right dot"
        },
        "components_with_assumptions": {
            "rink": {
                "view": "offensive",
                "assumption": "Offensive zone view for faceoff at right dot",
                "confidence": 0.95
            },
            "players": [
                {
                    "id": "C",
                    "type": "center",
                    "team": "home",
                    "position_desc": "at right faceoff dot in offensive zone",
                    "assumption": "Center taking faceoff",
                    "confidence": 1.0
                },
                {
                    "id": "LW",
                    "type": "winger",
                    "team": "home", 
                    "position_desc": "left winger on faceoff circle",
                    "assumption": "Standard faceoff formation",
                    "confidence": 0.9
                },
                {
                    "id": "RW",
                    "type": "winger",
                    "team": "home",
                    "position_desc": "right winger on faceoff circle",
                    "assumption": "Standard faceoff formation",
                    "confidence": 0.9
                },
                {
                    "id": "LD",
                    "type": "defense",
                    "team": "home",
                    "position_desc": "left defenseman at left point",
                    "assumption": "Positioned to receive win-back pass",
                    "confidence": 0.95
                },
                {
                    "id": "RD",
                    "type": "defense",
                    "team": "home",
                    "position_desc": "right defenseman at right point",
                    "assumption": "Standard offensive zone positioning",
                    "confidence": 0.9
                },
                {
                    "id": "G",
                    "type": "goalie",
                    "team": "away",
                    "position_desc": "opposing goalie in net",
                    "assumption": "Defending against the shot",
                    "confidence": 1.0
                }
            ],
            "movements": [
                {
                    "id": "m1",
                    "type": "pass",
                    "desc": "center wins faceoff back to left defenseman",
                    "from_player": "C",
                    "to_player": "LD",
                    "to_area": "left point",
                    "assumption": "Clean win back to the point",
                    "confidence": 0.9
                },
                {
                    "id": "m2", 
                    "type": "shot",
                    "desc": "left defenseman takes slap shot on goal",
                    "from_player": "LD",
                    "to_area": "on net",
                    "assumption": "Direct shot on goal after receiving pass",
                    "confidence": 0.95
                }
            ],
            "zones": [],
            "annotations": [
                {
                    "text": "Offensive Zone Faceoff - Win Back & Shoot",
                    "position_desc": "title",
                    "assumption": "Title for the play",
                    "confidence": 1.0
                }
            ],
            "equipment": []
        },
        "questions_for_user": [],
        "metadata": {
            "type": "play",
            "phase": "offensive",
            "key_players": ["C", "LD"]
        }
    }
    
    print("\n2. Analysis complete (manual creation to bypass MCP issue)")
    print(f"   Players: {len(analysis['components_with_assumptions']['players'])}")
    print(f"   Movements: {len(analysis['components_with_assumptions']['movements'])}")
    
    # Step 2: Translate to spec
    print("\n3. Translating to diagram spec...")
    result = translate_analysis_to_spec(
        analysis=analysis,
        title="Offensive Zone Faceoff Play",
        description="Win back to defense for shot on goal"
    )
    
    if result.get("success"):
        spec = result["spec"]
        print(f"   ✅ Spec created successfully")
        print(f"   Players mapped: {len(spec.get('players', []))}")
        print(f"   Movements mapped: {len(spec.get('movements', []))}")
        
        # Show player positions
        print("\n4. Player Positions:")
        for player in spec.get("players", []):
            coords = player.get("coordinates", {})
            print(f"   {player.get('label', player.get('id'))}: ({coords.get('x')}, {coords.get('y')})")
        
        # Show movements
        print("\n5. Movements:")
        for movement in spec.get("movements", []):
            print(f"   {movement.get('type')}: {movement.get('from', {})} → {movement.get('to', {})}")
            if movement.get("waypoints"):
                print(f"      Waypoints: {movement.get('waypoints')}")
        
        # Step 3: Generate diagram
        print("\n6. Generating diagram...")
        gen_result = generate_diagram(spec, output_name="faceoff_shot_play")
        
        if gen_result.get("success"):
            print(f"   ✅ Diagram saved to: {gen_result.get('image_path')}")
            print(f"   Elements: {gen_result.get('element_count')}")
        else:
            print(f"   ❌ Generation failed: {gen_result.get('error')}")
            
        return spec
    else:
        print(f"   ❌ Translation failed: {result.get('error')}")
        return None

if __name__ == "__main__":
    spec = test_faceoff_shot()
    if spec:
        print("\n" + "=" * 80)
        print("✅ Test complete!")
        print("=" * 80)