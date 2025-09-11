#!/usr/bin/env python3
"""Test the movement mapping with LLM and curve generation."""

import sys
import os
import json
from pathlib import Path
import logging

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'servers'))

from hockey_diagram_mcp_v3 import map_movements_with_llm

def test_movement_mapping():
    """Test movement mapping with LLM and curve generation."""
    
    # Test scenarios with different movement types
    test_scenarios = [
        {
            "name": "Basic Pass and Skate",
            "view": "offensive",
            "players": [
                {"id": "C", "position": "C", "coordinates": {"x": 69, "y": 22.5}, "type": "center", "team": "home", "label": "C"},
                {"id": "LW", "position": "LW", "coordinates": {"x": 75, "y": 38}, "type": "forward", "team": "home", "label": "LW"},
                {"id": "RW", "position": "RW", "coordinates": {"x": 85, "y": 0}, "type": "forward", "team": "home", "label": "RW"},
            ],
            "movements": [
                {
                    "id": "m1",
                    "type": "pass",
                    "player_id": "C",
                    "description": "Pass from center to left wing on the half wall"
                },
                {
                    "id": "m2",
                    "type": "skate",
                    "player_id": "LW",
                    "description": "Left wing drives to the net"
                }
            ]
        },
        {
            "name": "Behind Net Play",
            "view": "offensive",
            "players": [
                {"id": "C", "coordinates": {"x": 75, "y": 0}, "type": "center", "team": "home", "label": "C"},
                {"id": "RW", "coordinates": {"x": 89, "y": -36}, "type": "forward", "team": "home", "label": "RW"},
            ],
            "movements": [
                {
                    "id": "m1",
                    "type": "carry",
                    "player_id": "C",
                    "description": "Center carries puck behind the net for a wraparound"
                },
                {
                    "id": "m2",
                    "type": "pass",
                    "player_id": "C",
                    "description": "Pass from behind net to right wing in corner"
                }
            ]
        },
        {
            "name": "Circle Drill",
            "view": "offensive",
            "players": [
                {"id": "F1", "coordinates": {"x": 69, "y": 30}, "type": "forward", "team": "home", "label": "F1"},
                {"id": "F2", "coordinates": {"x": 69, "y": 15}, "type": "forward", "team": "home", "label": "F2"},
            ],
            "movements": [
                {
                    "id": "m1",
                    "type": "skate",
                    "player_id": "F1",
                    "description": "Skate around the right faceoff circle back to starting position"
                },
                {
                    "id": "m2",
                    "type": "skate",
                    "player_id": "F2",
                    "description": "Tight turn at the dot and return"
                }
            ]
        },
        {
            "name": "Rush with Bank Pass",
            "view": "neutral",
            "players": [
                {"id": "D", "coordinates": {"x": -25, "y": 0}, "type": "defense", "team": "home", "label": "D"},
                {"id": "F", "coordinates": {"x": 0, "y": 20}, "type": "forward", "team": "home", "label": "F"},
            ],
            "movements": [
                {
                    "id": "m1",
                    "type": "pass",
                    "player_id": "D",
                    "description": "Bank pass off the boards to forward in neutral zone"
                },
                {
                    "id": "m2",
                    "type": "skate",
                    "player_id": "F",
                    "description": "Forward rushes up ice toward offensive zone"
                }
            ]
        },
        {
            "name": "Cycle and Turn Drill",
            "view": "offensive",
            "players": [
                {"id": "F1", "coordinates": {"x": 89, "y": 36}, "type": "forward", "team": "home", "label": "F1"},
                {"id": "F2", "coordinates": {"x": 54, "y": 0}, "type": "forward", "team": "home", "label": "F2"},
            ],
            "movements": [
                {
                    "id": "m1",
                    "type": "carry",
                    "player_id": "F1",
                    "description": "Cycle along the boards from corner"
                },
                {
                    "id": "m2",
                    "type": "skate",
                    "player_id": "F2",
                    "description": "Gradual sweeping turn back toward defensive zone"
                }
            ]
        }
    ]
    
    print("=" * 80)
    print("MOVEMENT MAPPING TEST WITH LLM")
    print("=" * 80)
    print("\nTesting curve generation and spatial awareness\n")
    
    for scenario in test_scenarios:
        print(f"\n{'='*70}")
        print(f"📋 SCENARIO: {scenario['name']}")
        print(f"   View: {scenario['view']}")
        print(f"{'='*70}")
        
        # Map movements using LLM
        result = map_movements_with_llm(
            scenario["movements"],
            scenario["players"],
            scenario["view"]
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            continue
        
        if "movements_mapped" in result:
            print(f"\n{'Movement':<8} {'Type':<8} {'From':<15} {'To':<15} {'Waypoints':<10} {'Curve':<12} {'Confidence':<10}")
            print("-" * 90)
            
            for movement in result["movements_mapped"]:
                mov_id = movement.get("id", "N/A")
                mov_type = movement.get("type", "N/A")
                
                # Format start position
                start = movement.get("start", {})
                start_str = f"({start.get('x', 0):5.1f},{start.get('y', 0):5.1f})"
                
                # Format end position
                end = movement.get("end", {})
                end_str = f"({end.get('x', 0):5.1f},{end.get('y', 0):5.1f})"
                
                # Count waypoints
                waypoints = movement.get("waypoints", [])
                wp_count = len(waypoints)
                
                # Path type
                path_type = movement.get("path_type", "unknown")
                
                # Confidence
                confidence = movement.get("confidence", 0)
                
                print(f"{mov_id:<8} {mov_type:<8} {start_str:<15} {end_str:<15} {wp_count:<10} {path_type:<12} {confidence:.2f}")
                
                # Show waypoints if present
                if waypoints:
                    print(f"         Waypoints: ", end="")
                    for i, wp in enumerate(waypoints):
                        print(f"({wp.get('x', 0):.1f},{wp.get('y', 0):.1f})", end="")
                        if i < len(waypoints) - 1:
                            print(" → ", end="")
                    print()
                
                # Show reasoning for low confidence
                if confidence < 0.8 and movement.get("reasoning"):
                    print(f"         Reasoning: {movement['reasoning'][:60]}...")
                
                # Show any warnings
                if movement.get("warnings"):
                    print(f"         ⚠️ Warnings: {', '.join(movement['warnings'])}")
        
        # Show path validation results
        if "path_validation" in result:
            validation = result["path_validation"]
            if validation.get("through_net_issues"):
                print(f"\n❌ Paths through net: {', '.join(validation['through_net_issues'])}")
            if validation.get("out_of_bounds"):
                print(f"\n❌ Out of bounds: {', '.join(validation['out_of_bounds'])}")
            if validation.get("unrealistic_paths"):
                print(f"\n⚠️ Unrealistic paths: {', '.join(validation['unrealistic_paths'])}")
        
        # Show questions
        if "questions_for_user" in result and result["questions_for_user"]:
            print("\n❓ Questions for clarification:")
            for q in result["questions_for_user"]:
                print(f"   - {q['question']}")
                if q.get("impact"):
                    print(f"     Impact: {q['impact']}")

    print("\n" + "=" * 80)
    print("CURVE TYPE ANALYSIS:")
    print("-" * 80)
    print("Expected curve types by scenario:")
    print("  1. Basic Pass: 'standard' with minimal curve for pass")
    print("  2. Behind Net: 'behind_net' with waypoints around net")
    print("  3. Circle Drill: 'circle' following faceoff circle")
    print("  4. Bank Pass: 'bank' with board reflection point")
    print("  5. Cycle: 'cycle' along boards")
    print("\nCheck logs for:")
    print("  - suggest_curve_type calls")
    print("  - generate_curve_waypoints calls")
    print("  - validate_path calls (if any)")
    print("=" * 80)

def check_latest_log():
    """Check the latest log for function calls and errors."""
    import subprocess
    import time
    
    # Wait a moment for logs to be written
    time.sleep(1)
    
    print("\n" + "=" * 80)
    print("CHECKING LATEST LOG FILE:")
    print("-" * 80)
    
    # Find the latest log file
    log_dir = Path(__file__).parent / "logs"
    if log_dir.exists():
        log_files = sorted(log_dir.glob("hockey_diagram_mcp_*.log"), key=lambda x: x.stat().st_mtime)
        if log_files:
            latest_log = log_files[-1]
            print(f"Latest log: {latest_log.name}")
            
            # Extract function calls from log
            with open(latest_log, 'r') as f:
                lines = f.readlines()
            
            # Count function calls
            function_counts = {
                "suggest_curve_type": 0,
                "generate_curve_waypoints": 0,
                "validate_path": 0,
                "get_zone_boundaries": 0,
                "list_available_zones": 0
            }
            
            errors = []
            
            for line in lines:
                # Count function calls
                for func_name in function_counts:
                    if func_name in line and ("Executed" in line or "Suggested" in line or "Generated" in line or "Validated" in line):
                        function_counts[func_name] += 1
                
                # Check for errors
                if "ERROR" in line or "Failed" in line:
                    errors.append(line.strip())
            
            print("\nFunction Call Summary:")
            for func_name, count in function_counts.items():
                if count > 0:
                    print(f"  {func_name:30} : {count} calls")
            
            if errors:
                print("\n⚠️ Errors Found:")
                for error in errors[:5]:  # Show first 5 errors
                    print(f"  - {error[:100]}...")
            else:
                print("\n✅ No errors found in log")
            
            # Show last few lines of log
            print("\nLast 10 log entries:")
            print("-" * 40)
            for line in lines[-10:]:
                if line.strip():
                    # Truncate long lines
                    print(f"  {line.strip()[:100]}")
    else:
        print("No log directory found")
    
    print("=" * 80)

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Set logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set in environment")
        sys.exit(1)
    
    test_movement_mapping()
    check_latest_log()