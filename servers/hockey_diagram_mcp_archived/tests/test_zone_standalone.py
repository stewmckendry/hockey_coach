#!/usr/bin/env python3
"""
Standalone test for zone-based coordinate mapper without dependencies.
"""

import sys
sys.path.append('.')

from coordinate_mapper import get_player_coordinate, get_formation_coordinates, get_zone_by_coordinate

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

def test_formation_semantics():
    """Test that formation assignments make tactical sense."""
    print("=== Formation Semantic Test ===")
    
    # Test box penalty kill 
    box_coords = get_formation_coordinates("box_penalty_kill")
    if box_coords:
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
    print("Zone-Based Coordinate Mapper - Standalone Test")
    print("=" * 50)
    
    test_coordinate_reasonableness()
    test_formation_semantics()
    
    print("=" * 50)
    print("Standalone test complete!")