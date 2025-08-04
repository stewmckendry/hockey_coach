#!/usr/bin/env python3
"""
Comprehensive test suite for the zone-based coordinate mapper refactor.
Tests all major functionality including zone mappings, formations, and backwards compatibility.
"""

import sys
sys.path.append('.')

from coordinate_mapper import (
    coordinate_mapper,
    get_player_coordinate,
    get_formation_coordinates,
    get_zone_coordinate,
    list_available_zones,
    get_zone_by_coordinate,
    Zone
)

def test_zone_coverage():
    """Test that all zones are correctly covered."""
    print("=== Zone Coverage Test ===")
    
    zones = list_available_zones()
    print(f"Total zones: {len(zones)}")
    
    # Should have 32 zones total (6 def + 6 off + 8 neu + 6 def + 6 off)
    # Actually: 12 def + 12 off + 8 neu = 32 zones
    expected_zones = 32
    if len(zones) == expected_zones:
        print(f"✓ Zone count correct: {len(zones)} zones")
    else:
        print(f"✗ Zone count incorrect: expected {expected_zones}, got {len(zones)}")
    
    # Check zone naming patterns
    def_zones = [z for z in zones if z.startswith('def-')]
    off_zones = [z for z in zones if z.startswith('off-')]
    neu_zones = [z for z in zones if z.startswith('neu-')]
    
    print(f"Defensive zones: {len(def_zones)}")
    print(f"Offensive zones: {len(off_zones)}")
    print(f"Neutral zones: {len(neu_zones)}")
    
    # Test coordinate bounds
    for zone in zones[:5]:  # Test first 5 zones
        coord = get_zone_coordinate(zone)
        print(f"  {zone}: {coord}")
        
        # Verify coordinates are within NHL rink bounds
        if -100 <= coord[0] <= 100 and -42.5 <= coord[1] <= 42.5:
            print(f"    ✓ Within bounds")
        else:
            print(f"    ✗ Outside bounds!")
    
    print()

def test_position_mappings():
    """Test individual position mappings to zones."""
    print("=== Position Mapping Test ===")
    
    test_cases = [
        ("C", "offensive", "primary"),
        ("C", "defensive", "faceoff"), 
        ("LW", "offensive", "corner"),
        ("LW", "defensive", "point"),
        ("RW", "neutral", "wing"),
        ("LD", "offensive", "point"),
        ("RD", "defensive", "net_front"),
        ("G", "defensive", "primary"),
    ]
    
    all_passed = True
    for position, zone, role in test_cases:
        coord = get_player_coordinate(position, zone, role)
        zone_name = get_zone_by_coordinate(coord[0], coord[1])
        
        # Verify coordinate is reasonable
        if -100 <= coord[0] <= 100 and -42.5 <= coord[1] <= 42.5:
            status = "✓"
        else:
            status = "✗"
            all_passed = False
            
        print(f"  {status} {position} {zone} {role}: {coord} -> {zone_name}")
    
    if all_passed:
        print("✓ All position mappings within bounds")
    else:
        print("✗ Some position mappings out of bounds")
    
    print()

def test_formation_mappings():
    """Test formation-specific mappings."""
    print("=== Formation Mapping Test ===")
    
    formations = [
        "box_penalty_kill",
        "diamond_penalty_kill", 
        "1-3-1_powerplay",
        "2-1-2_forecheck",
        "breakout_strong_side",
        "cycle_offensive_zone"
    ]
    
    for formation in formations:
        print(f"  {formation}:")
        coords = get_formation_coordinates(formation)
        
        if not coords:
            print(f"    ✗ No coordinates returned")
            continue
            
        valid_formation = True
        for role, coord in coords.items():
            zone_name = get_zone_by_coordinate(coord[0], coord[1])
            
            # Check bounds
            if not (-100 <= coord[0] <= 100 and -42.5 <= coord[1] <= 42.5):
                valid_formation = False
                status = "✗"
            else:
                status = "✓"
                
            print(f"    {status} {role}: {coord} -> {zone_name}")
        
        if valid_formation:
            print(f"    ✓ Formation valid")
        else:
            print(f"    ✗ Formation has invalid coordinates")
        print()

def test_special_cases():
    """Test special cases and edge conditions."""
    print("=== Special Cases Test ===")
    
    # Test box penalty kill specific requirements
    print("1. Box penalty kill D1/D2 positioning:")
    box_coords = get_formation_coordinates("box_penalty_kill")
    
    if "low_left" in box_coords and "low_right" in box_coords:
        low_left_zone = get_zone_by_coordinate(box_coords["low_left"][0], box_coords["low_left"][1])
        low_right_zone = get_zone_by_coordinate(box_coords["low_right"][0], box_coords["low_right"][1])
        
        # Both should be in defensive center zones (in front of net)
        if "def-center" in low_left_zone and "def-center" in low_right_zone:
            print("  ✓ D1/D2 correctly positioned in front of net")
        else:
            print("  ✗ D1/D2 not positioned in front of net")
            print(f"    low_left: {low_left_zone}, low_right: {low_right_zone}")
    else:
        print("  ✗ Box formation missing low positions")
    
    # Test 2-1-2 forecheck F3 positioning 
    print("2. 2-1-2 forecheck F3 positioning:")
    forecheck_coords = get_formation_coordinates("2-1-2_forecheck")
    
    if "F3" in forecheck_coords:
        f3_zone = get_zone_by_coordinate(forecheck_coords["F3"][0], forecheck_coords["F3"][1])
        if "neu-" in f3_zone:  # Should be in neutral zone
            print("  ✓ F3 correctly positioned in neutral zone")
        else:
            print(f"  ✗ F3 not in neutral zone: {f3_zone}")
    else:
        print("  ✗ 2-1-2 formation missing F3")
    
    # Test goalie positioning consistency
    print("3. Goalie positioning consistency:")
    goalie_zones = ["offensive", "defensive", "neutral"]
    goalie_coords = []
    
    for zone in goalie_zones:
        coord = get_player_coordinate("G", zone, "primary")
        goalie_coords.append(coord)
        zone_name = get_zone_by_coordinate(coord[0], coord[1])
        print(f"  Goalie in {zone}: {coord} -> {zone_name}")
    
    # All goalie positions should be the same (in net)
    if len(set(goalie_coords)) == 1:
        print("  ✓ Goalie consistently positioned")
    else:
        print("  ✗ Goalie positioning inconsistent")
    
    print()

def test_backwards_compatibility():
    """Test backwards compatibility with legacy system."""
    print("=== Backwards Compatibility Test ===")
    
    # Test that zone-based system provides reasonable coordinates
    # compared to legacy hardcoded system
    test_positions = [
        ("C", "offensive", "primary"),
        ("LW", "defensive", "corner"),
        ("RD", "neutral", "gap")
    ]
    
    for position, zone, role in test_positions:
        zone_coord = get_player_coordinate(position, zone, role)
        
        # Try to get legacy coordinate
        zone_enum = Zone.DEFENSIVE if zone == "defensive" else Zone.OFFENSIVE if zone == "offensive" else Zone.NEUTRAL
        legacy_coord = None
        
        if hasattr(coordinate_mapper, 'POSITION_COORDINATES'):
            legacy_coord = coordinate_mapper.POSITION_COORDINATES.get(position, {}).get(zone_enum, {}).get(role)
        
        print(f"  {position} {zone} {role}:")
        print(f"    Zone-based: {zone_coord}")
        if legacy_coord:
            print(f"    Legacy:     {legacy_coord}")
            
            # Calculate distance between zone and legacy
            distance = ((zone_coord[0] - legacy_coord[0])**2 + (zone_coord[1] - legacy_coord[1])**2)**0.5
            print(f"    Distance:   {distance:.1f} units")
            
            if distance < 50:  # Reasonable proximity 
                print(f"    ✓ Close to legacy position")
            else:
                print(f"    ⚠ Significant difference from legacy")
        else:
            print(f"    Legacy:     Not found")
    
    print()

def test_zone_grid_integration():
    """Test integration with ZoneGrid system."""
    print("=== Zone Grid Integration Test ===")
    
    from zone_grid import zone_grid
    
    # Test that coordinate mapper zones match zone grid zones
    mapper_zones = set(list_available_zones())
    grid_zones = set(zone_grid.list_all_zones())
    
    if mapper_zones == grid_zones:
        print("✓ Coordinate mapper zones match zone grid")
    else:
        print("✗ Zone mismatch between mapper and grid")
        missing_in_mapper = grid_zones - mapper_zones
        missing_in_grid = mapper_zones - grid_zones
        if missing_in_mapper:
            print(f"  Missing in mapper: {missing_in_mapper}")
        if missing_in_grid:
            print(f"  Missing in grid: {missing_in_grid}")
    
    # Test coordinate consistency 
    test_zones = ["def-left-low", "off-right-high", "neu-left-mid-high", "def-center-right-low"]
    
    for zone_name in test_zones:
        mapper_coord = get_zone_coordinate(zone_name)
        grid_coord = zone_grid.get_zone_position(zone_name)
        
        if mapper_coord == grid_coord:
            print(f"  ✓ {zone_name}: coordinates match")
        else:
            print(f"  ✗ {zone_name}: coordinates differ")
            print(f"    Mapper: {mapper_coord}")
            print(f"    Grid:   {grid_coord}")
    
    print()

if __name__ == "__main__":
    print("Hockey Diagram Zone-Based Coordinate Mapper - Comprehensive Test Suite")
    print("=" * 70)
    
    test_zone_coverage()
    test_position_mappings() 
    test_formation_mappings()
    test_special_cases()
    test_backwards_compatibility()
    test_zone_grid_integration()
    
    print("=" * 70)
    print("Test suite complete!")