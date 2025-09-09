#!/usr/bin/env python3
"""Test player position mapping issues."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'servers'))

from hockey_diagram_mcp_v3 import map_hockey_position

def test_positions():
    """Test various position descriptions."""
    
    test_cases = [
        # Format: (position_desc, zone, expected_coords, description)
        ("left neutral dot", "neutral", {"x": 20, "y": 22.5}, "Should be at (20, 22.5) for offensive-side neutral dot"),
        ("right neutral dot", "neutral", {"x": 20, "y": -22.5}, "Should be at (20, -22.5) for offensive-side neutral dot"),
        ("left neutral dot", "full", None, "Full view - should use neutral zone defaults?"),
        ("net", "offensive", None, "Where is the net?"),
        ("in net", "offensive", None, "Goalie in net"),
        ("center ice near offensive blue line", "neutral", None, "D1 position from our test"),
        ("offensive blue line", "neutral", None, "Blue line position"),
    ]
    
    print("Testing Player Position Mapping\n" + "="*50)
    
    for pos_desc, zone, expected, note in test_cases:
        result = map_hockey_position(pos_desc, zone)
        
        if expected:
            match = result == expected
            status = "✅" if match else "❌"
            print(f"{status} {pos_desc:40} → {result}")
            if not match:
                print(f"    Expected: {expected}")
        else:
            print(f"🔍 {pos_desc:40} → {result}")
        
        if note:
            print(f"    Note: {note}")
        print()
    
    # Test the actual 2v1 positions we used
    print("\nTesting 2v1 Rush Drill Positions")
    print("-"*50)
    
    drill_positions = [
        ("left neutral dot", "neutral"),
        ("right neutral dot", "neutral"),
        ("center ice near offensive blue line", "neutral"),
        ("net", "offensive"),
    ]
    
    for desc, zone in drill_positions:
        result = map_hockey_position(desc, zone)
        print(f"{desc:40} [{zone:10}] → {result}")

if __name__ == "__main__":
    test_positions()