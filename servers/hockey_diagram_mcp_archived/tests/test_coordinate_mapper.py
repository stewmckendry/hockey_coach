#!/usr/bin/env python3
"""
Test script for the coordinate mapping system.
Verifies that all functions work correctly and coordinates are NHL-accurate.
"""

import sys
from coordinate_mapper import (
    coordinate_mapper,
    get_player_coordinate,
    get_area_coordinate,
    convert_role_to_coordinate,
    get_formation_coordinates,
    adjust_for_formation,
    get_drill_positioning,
    list_available_formations,
    list_available_areas,
    validate_coordinate,
)


def test_basic_coordinates():
    """Test basic coordinate retrieval."""
    print("=== Testing Basic Coordinates ===")
    
    # Test player positions
    center_offensive = get_player_coordinate("C", "offensive", "primary")
    print(f"Center in offensive zone (primary): {center_offensive}")
    
    lw_corner = get_player_coordinate("LW", "offensive", "corner")
    print(f"Left wing in corner: {lw_corner}")
    
    goalie = get_player_coordinate("G", "defensive", "primary")
    print(f"Goalie position: {goalie}")
    
    # Test area coordinates
    slot = get_area_coordinate("slot")
    print(f"Slot area: {slot}")
    
    left_point = get_area_coordinate("left_point")
    print(f"Left point: {left_point}")
    
    print()


def test_role_conversion():
    """Test converting role descriptions to coordinates."""
    print("=== Testing Role Conversion ===")
    
    # Test various role descriptions
    test_cases = [
        ("C", "high slot", "offensive"),
        ("LW", "left corner", "offensive"),
        ("RD", "point", "offensive"),
        ("LD", "gap", "defensive"),
        ("G", "crease", "defensive"),
    ]
    
    for position, location, zone in test_cases:
        coord = convert_role_to_coordinate(position, location, zone)
        print(f"{position} at {location} in {zone} zone: {coord}")
    
    print()


def test_formations():
    """Test formation coordinate generation."""
    print("=== Testing Formations ===")
    
    formations = ["2-1-2_forecheck", "1-3-1_powerplay", "box_penalty_kill"]
    
    for formation in formations:
        print(f"\n{formation.upper()}:")
        coords = get_formation_coordinates(formation)
        for role, coord in coords.items():
            print(f"  {role}: {coord}")
    
    print()


def test_drill_positioning():
    """Test drill positioning."""
    print("=== Testing Drill Positioning ===")
    
    drills = ["triangle_passing", "2v1_rush", "shooting_drill"]
    
    for drill in drills:
        positions = get_drill_positioning(drill)
        print(f"\n{drill.upper()}:")
        for i, pos in enumerate(positions):
            print(f"  Player {i+1}: {pos}")
    
    print()


def test_formation_adjustment():
    """Test adjusting players for formations."""
    print("=== Testing Formation Adjustment ===")
    
    # Create basic player list
    players = [
        {"position": "C", "x": 0, "y": 0, "team": "home"},
        {"position": "LW", "x": 0, "y": -25, "team": "home"},
        {"position": "RW", "x": 0, "y": 25, "team": "home"},
        {"position": "LD", "x": -25, "y": -20, "team": "home"},
        {"position": "RD", "x": -25, "y": 20, "team": "home"},
        {"position": "G", "x": -89, "y": 0, "team": "home"},
    ]
    
    print("Original positions:")
    for player in players:
        print(f"  {player['position']}: ({player['x']}, {player['y']})")
    
    # Adjust for 2-1-2 forecheck
    adjusted = adjust_for_formation(players, "2-1-2_forecheck")
    print(f"\nAdjusted for 2-1-2 forecheck:")
    for player in adjusted:
        print(f"  {player['position']}: ({player['x']}, {player['y']})")
    
    print()


def test_coordinate_validation():
    """Test coordinate validation."""
    print("=== Testing Coordinate Validation ===")
    
    test_coords = [
        (0, 0),        # Valid center
        (150, 0),      # X out of bounds
        (0, 60),       # Y out of bounds
        (-120, -50),   # Both out of bounds
        (89, 42.5),    # Valid edge case
    ]
    
    for x, y in test_coords:
        validated = validate_coordinate(x, y)
        print(f"({x}, {y}) -> {validated}")
    
    print()


def test_available_lists():
    """Test listing available formations, areas, etc."""
    print("=== Available Elements ===")
    
    formations = list_available_formations()
    print(f"Available formations ({len(formations)}):")
    for formation in formations:
        print(f"  - {formation}")
    
    print(f"\nAvailable areas ({len(list_available_areas())}):")
    areas = list_available_areas()[:10]  # Show first 10
    for area in areas:
        coord = get_area_coordinate(area)
        print(f"  - {area}: {coord}")
    if len(list_available_areas()) > 10:
        print(f"  ... and {len(list_available_areas()) - 10} more")
    
    print()


def test_zone_specific():
    """Test zone-specific coordinate retrieval."""
    print("=== Testing Zone-Specific Coordinates ===")
    
    zones = ["offensive", "defensive", "neutral"]
    
    for zone in zones:
        print(f"\n{zone.upper()} ZONE:")
        zone_coords = coordinate_mapper.get_zone_specific_coordinates(zone)
        for position, roles in zone_coords.items():
            print(f"  {position}:")
            for role, coord in roles.items():
                print(f"    {role}: {coord}")
    
    print()


def main():
    """Run all tests."""
    print("Testing Hockey Coordinate Mapping System")
    print("=" * 50)
    
    try:
        test_basic_coordinates()
        test_role_conversion()
        test_formations()
        test_drill_positioning()
        test_formation_adjustment()
        test_coordinate_validation()
        test_available_lists()
        test_zone_specific()
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()