#!/usr/bin/env python3
"""
Integration test for zone-based coordinate mapper with the hockey diagram system.
"""

import sys
sys.path.append('.')

from coordinate_mapper import get_player_coordinate, get_formation_coordinates
from two_stage_parser import TwoStageParser

def test_parser_integration():
    """Test that the updated coordinate mapper works with the two-stage parser."""
    print("=== Parser Integration Test ===")
    
    # Test simple formation
    prompt = "Box penalty kill formation with defensemen in front of net"
    
    parser = TwoStageParser()
    try:
        result = parser.parse_prompt(prompt)
        
        if result and 'players' in result:
            print(f"✓ Parser successfully processed: '{prompt}'")
            print(f"  Found {len(result['players'])} players")
            
            # Check that coordinates are reasonable
            for player in result['players']:
                if 'x' in player and 'y' in player:
                    x, y = player['x'], player['y']
                    if -100 <= x <= 100 and -42.5 <= y <= 42.5:
                        print(f"  ✓ Player {player.get('position', '?')}: ({x}, {y}) - within bounds")
                    else:
                        print(f"  ✗ Player {player.get('position', '?')}: ({x}, {y}) - out of bounds")
                else:
                    print(f"  ⚠ Player missing coordinates: {player}")
        else:
            print(f"✗ Parser failed to process prompt")
            
    except Exception as e:
        print(f"✗ Parser integration failed: {e}")
    
    print()

def test_coordinate_reasonableness():
    """Test that all zone-based coordinates are reasonable for hockey."""
    print("=== Coordinate Reasonableness Test ===")
    
    formations_to_test = [
        "box_penalty_kill",
        "1-3-1_powerplay", 
        "2-1-2_forecheck"
    ]
    
    for formation in formations_to_test:
        print(f"Testing {formation}:")
        coords = get_formation_coordinates(formation)
        
        if not coords:
            print(f"  ✗ No coordinates found")
            continue
        
        # Analyze coordinate distribution
        x_coords = [coord[0] for coord in coords.values()]
        y_coords = [coord[1] for coord in coords.values()]
        
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        
        print(f"  X range: {min(x_coords):.1f} to {max(x_coords):.1f} ({x_range:.1f} units)")
        print(f"  Y range: {min(y_coords):.1f} to {max(y_coords):.1f} ({y_range:.1f} units)")
        
        # Check for reasonable spread
        if x_range > 10 and y_range > 10:
            print(f"  ✓ Good spatial distribution")
        else:
            print(f"  ⚠ Limited spatial distribution")
        
        # Check for clustering (players too close together)
        min_distance = float('inf')
        for i, (role1, coord1) in enumerate(coords.items()):
            for j, (role2, coord2) in enumerate(coords.items()):
                if i < j:  # Avoid duplicates
                    dist = ((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)**0.5
                    min_distance = min(min_distance, dist)
        
        if min_distance > 5:  # Players should be at least 5 units apart
            print(f"  ✓ No player clustering (min distance: {min_distance:.1f})")
        else:
            print(f"  ⚠ Players may be too close (min distance: {min_distance:.1f})")
        
        print()

def test_zone_semantic_correctness():
    """Test that zone assignments make semantic sense."""
    print("=== Zone Semantic Correctness Test ===")
    
    # Test individual position semantics
    semantic_tests = [
        # (position, zone, role, expected_zone_pattern)
        ("G", "defensive", "primary", "def-center-right-low"),  # Goalie in net
        ("C", "offensive", "faceoff", "off-center"),  # Center in offensive faceoff
        ("LW", "offensive", "corner", "off-center-left-low"),  # LW in corner
        ("RD", "defensive", "point", "def-"),  # RD on point
        ("LD", "neutral", "gap", "neu-"),  # LD in neutral zone gap
    ]
    
    for position, zone, role, expected_pattern in semantic_tests:
        coord = get_player_coordinate(position, zone, role)
        
        # Get the actual zone name
        from coordinate_mapper import get_zone_by_coordinate
        actual_zone = get_zone_by_coordinate(coord[0], coord[1])
        
        if expected_pattern in actual_zone:
            print(f"  ✓ {position} {zone} {role}: {actual_zone} (matches {expected_pattern})")
        else:
            print(f"  ✗ {position} {zone} {role}: {actual_zone} (expected {expected_pattern})")
    
    print()

def test_formation_semantics():
    """Test that formation assignments make tactical sense."""
    print("=== Formation Semantic Test ===")
    
    # Test box penalty kill 
    box_coords = get_formation_coordinates("box_penalty_kill")
    if box_coords:
        from coordinate_mapper import get_zone_by_coordinate
        
        print("Box penalty kill analysis:")
        for role, coord in box_coords.items():
            zone = get_zone_by_coordinate(coord[0], coord[1])
            
            if role.startswith("high"):
                if "mid-high" in zone or "high" in zone:
                    print(f"  ✓ {role}: {zone} (correctly high)")
                else:
                    print(f"  ⚠ {role}: {zone} (should be higher)")
            elif role.startswith("low"):
                if "low" in zone:
                    print(f"  ✓ {role}: {zone} (correctly low)")
                else:
                    print(f"  ⚠ {role}: {zone} (should be lower)")
    
    # Test 2-1-2 forecheck
    forecheck_coords = get_formation_coordinates("2-1-2_forecheck")
    if forecheck_coords:
        print("2-1-2 forecheck analysis:")
        for role, coord in forecheck_coords.items():
            zone = get_zone_by_coordinate(coord[0], coord[1])
            
            if role in ["F1", "F2"]:  # First two forwards
                if "off-" in zone:
                    print(f"  ✓ {role}: {zone} (correctly in offensive zone)")
                else:
                    print(f"  ⚠ {role}: {zone} (should be in offensive zone)")
            elif role == "F3":  # Third forward
                if "neu-" in zone:
                    print(f"  ✓ {role}: {zone} (correctly in neutral zone)")
                else:
                    print(f"  ⚠ {role}: {zone} (should be in neutral zone)")
            elif role in ["D1", "D2"]:  # Defense
                if "neu-" in zone or "def-" in zone:
                    print(f"  ✓ {role}: {zone} (correctly back)")
                else:
                    print(f"  ⚠ {role}: {zone} (should be back)")
    
    print()

if __name__ == "__main__":
    print("Zone-Based Coordinate Mapper - Integration Test Suite")
    print("=" * 60)
    
    test_parser_integration()
    test_coordinate_reasonableness()
    test_zone_semantic_correctness()
    test_formation_semantics()
    
    print("=" * 60)
    print("Integration test suite complete!")