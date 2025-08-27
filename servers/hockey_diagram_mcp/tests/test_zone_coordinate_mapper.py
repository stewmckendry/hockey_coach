#!/usr/bin/env python3
"""
Test script for the updated zone-based coordinate mapper.
"""

import sys
sys.path.append('.')

from coordinate_mapper import (
    coordinate_mapper, 
    get_player_coordinate, 
    get_formation_coordinates,
    get_zone_coordinate,
    list_available_zones,
    get_zone_by_coordinate
)

def test_zone_system():
    """Test the zone-based coordinate system."""
    print("=== Testing Zone-Based Coordinate Mapper ===\n")
    
    # Test 1: List available zones
    print("1. Available zones:")
    zones = list_available_zones()
    print(f"Total zones: {len(zones)}")
    for i, zone in enumerate(sorted(zones)):
        if i < 10:  # Show first 10
            coord = get_zone_coordinate(zone)
            print(f"  {zone}: {coord}")
    print(f"  ... and {len(zones) - 10} more zones\n")
    
    # Test 2: Test individual position mapping
    print("2. Individual position mapping:")
    test_cases = [
        ("C", "offensive", "primary"),
        ("LW", "offensive", "corner"),
        ("RD", "defensive", "net_front"),
        ("G", "defensive", "primary"),
    ]
    
    for position, zone, role in test_cases:
        coord = get_player_coordinate(position, zone, role)
        zone_name = get_zone_by_coordinate(coord[0], coord[1])
        print(f"  {position} {zone} {role}: {coord} -> zone: {zone_name}")
    print()
    
    # Test 3: Test formation coordinates
    print("3. Formation coordinates:")
    formations = ["box_penalty_kill", "2-1-2_forecheck", "1-3-1_powerplay"]
    
    for formation in formations:
        print(f"  {formation}:")
        coords = get_formation_coordinates(formation)
        for role, coord in coords.items():
            zone_name = get_zone_by_coordinate(coord[0], coord[1])
            print(f"    {role}: {coord} -> zone: {zone_name}")
        print()
    
    # Test 4: Compare zone-based vs legacy coordinates
    print("4. Zone-based vs Legacy comparison:")
    position = "LD"
    zone = "defensive" 
    role = "net_front"
    
    # Get coordinates using zone system
    zone_coord = get_player_coordinate(position, zone, role)
    zone_name = get_zone_by_coordinate(zone_coord[0], zone_coord[1])
    
    print(f"  {position} {zone} {role}:")
    print(f"    Zone-based: {zone_coord} -> zone: {zone_name}")
    
    # Test legacy fallback
    from coordinate_mapper import Zone
    coord_mapper = coordinate_mapper
    if hasattr(coord_mapper, 'POSITION_COORDINATES'):
        zone_enum = Zone.DEFENSIVE if zone == "defensive" else Zone.OFFENSIVE if zone == "offensive" else Zone.NEUTRAL
        legacy_coord = coord_mapper.POSITION_COORDINATES.get(position.upper(), {}).get(zone_enum, {}).get(role)
        if legacy_coord:
            print(f"    Legacy:     {legacy_coord}")
    print()
    
    # Test 5: Verify zone coverage
    print("5. Zone coverage verification:")
    test_positions = [
        (-87.5, -31.875),  # def-left-low
        (87.5, 31.875),    # off-right-high
        (-12.5, 0),        # neu-left-mid-low
        (12.5, 0),         # neu-right-mid-low
    ]
    
    for x, y in test_positions:
        zone_name = get_zone_by_coordinate(x, y)
        zone_center = get_zone_coordinate(zone_name)
        print(f"  ({x}, {y}) -> {zone_name} (center: {zone_center})")

def test_special_formations():
    """Test special formation handling."""
    print("\n=== Testing Special Formation Handling ===\n")
    
    # Test box penalty kill formation
    print("Box Penalty Kill Formation:")
    box_coords = get_formation_coordinates("box_penalty_kill")
    
    for role, coord in box_coords.items():
        zone_name = get_zone_by_coordinate(coord[0], coord[1])
        print(f"  {role}: {coord} -> zone: {zone_name}")
    
    # Verify D1/D2 are in front of net (specific requirement)
    if "low_left" in box_coords and "low_right" in box_coords:
        low_left_zone = get_zone_by_coordinate(box_coords["low_left"][0], box_coords["low_left"][1])
        low_right_zone = get_zone_by_coordinate(box_coords["low_right"][0], box_coords["low_right"][1])
        
        print(f"\n  ✓ Verification: D1/D2 in front of net")
        print(f"    low_left (LD) in zone: {low_left_zone}")
        print(f"    low_right (RD) in zone: {low_right_zone}")
        
        # Check if they're in defensive center zones (in front of net)
        if "def-center" in low_left_zone and "def-center" in low_right_zone:
            print("    ✓ Both defensemen correctly positioned in front of net")
        else:
            print("    ⚠ Defensemen may not be optimally positioned")

if __name__ == "__main__":
    test_zone_system()
    test_special_formations()
    print("\n=== Test Complete ===")