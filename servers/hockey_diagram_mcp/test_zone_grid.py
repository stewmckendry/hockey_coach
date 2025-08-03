#!/usr/bin/env python3
"""
Test script for the zone grid implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from zone_grid import ZoneGrid, get_zone_position, get_zone_by_position, get_adjacent_zones, get_zone_bounds

def test_zone_grid():
    """Test the zone grid implementation."""
    print("Testing Zone Grid Implementation")
    print("=" * 50)
    
    # Create zone grid instance
    grid = ZoneGrid()
    
    # Test 1: Verify we have 32 zones
    all_zones = grid.list_all_zones()
    print(f"✓ Total zones: {len(all_zones)} (expected: 32)")
    assert len(all_zones) == 32, f"Expected 32 zones, got {len(all_zones)}"
    
    # Test 2: Check zone distribution by area
    distribution = grid.get_zone_area_distribution()
    print(f"✓ Zone distribution: {distribution}")
    assert distribution["defensive"] == 12, f"Expected 12 defensive zones, got {distribution['defensive']}"
    assert distribution["neutral"] == 8, f"Expected 8 neutral zones, got {distribution['neutral']}"
    assert distribution["offensive"] == 12, f"Expected 12 offensive zones, got {distribution['offensive']}"
    
    # Test 3: Test zone position lookups
    print("\nTesting Zone Positions:")
    test_positions = [
        ("def-center-left-mid-low", (-62.5, -10.625)),
        ("neu-left-mid-low", (-12.5, -10.625)), 
        ("off-center-left-mid-low", (37.5, -10.625)),
        ("def-left-low", (-87.5, -31.875)),
        ("off-right-high", (87.5, 31.875))
    ]
    
    for zone_name, expected_pos in test_positions:
        actual_pos = get_zone_position(zone_name)
        print(f"  {zone_name}: {actual_pos} (expected: {expected_pos})")
        assert abs(actual_pos[0] - expected_pos[0]) < 1, f"X coordinate mismatch for {zone_name}"
        assert abs(actual_pos[1] - expected_pos[1]) < 1, f"Y coordinate mismatch for {zone_name}"
    
    # Test 4: Test position to zone lookup  
    print("\nTesting Position to Zone Lookup:")
    test_lookups = [
        ((-62.5, -10.625), "def-center-left-mid-low"),
        ((-12.5, -10.625), "neu-left-mid-low"),
        ((37.5, -10.625), "off-center-left-mid-low"),
        ((-87.5, -31.875), "def-left-low"),
        ((87.5, 31.875), "off-right-high")
    ]
    
    for pos, expected_zone in test_lookups:
        actual_zone = get_zone_by_position(pos[0], pos[1])
        print(f"  Position {pos}: {actual_zone} (expected: {expected_zone})")
        assert actual_zone == expected_zone, f"Zone lookup failed for position {pos}"
    
    # Test 5: Test zone bounds
    print("\nTesting Zone Bounds:")
    bounds = get_zone_bounds("def-center-left-mid-low")
    print(f"  def-center-left-mid-low bounds: {bounds}")
    assert bounds == (-75, -21.25, -50, 0), f"Incorrect bounds for def-center-left-mid-low"
    
    # Test 6: Test adjacency (spot check a few)
    print("\nTesting Zone Adjacency:")
    adjacent_to_center = get_adjacent_zones("neu-left-mid-low")
    print(f"  Zones adjacent to neu-left-mid-low: {len(adjacent_to_center)} zones")
    print(f"  Adjacent zones: {adjacent_to_center}")
    
    # This neutral zone should be adjacent to several zones
    assert len(adjacent_to_center) > 0, "Neutral zone should have adjacent zones"
    
    # Test 7: Test zone coverage (no gaps)
    print("\nTesting Zone Coverage:")
    test_points = [
        (-100, -42.5),  # Corner
        (-100, 42.5),   # Corner
        (100, -42.5),   # Corner  
        (100, 42.5),    # Corner
        (0, 0),         # Center
        (-50, 0),       # Defensive zone
        (50, 0),        # Offensive zone
        (-25, 0),       # Blue line
        (25, 0),        # Blue line
    ]
    
    for x, y in test_points:
        zone = get_zone_by_position(x, y)
        print(f"  Position ({x:4.1f}, {y:4.1f}): {zone}")
        assert zone is not None and zone != "", f"No zone found for position ({x}, {y})"
    
    # Test 8: Test offset positioning
    print("\nTesting Offset Positioning:")
    base_pos = get_zone_position("neu-center-ice")
    offset_pos = get_zone_position("neu-center-ice", offset_x=5, offset_y=-10)
    expected_offset = (base_pos[0] + 5, base_pos[1] - 10)
    print(f"  Base position: {base_pos}")
    print(f"  Offset position: {offset_pos} (expected: {expected_offset})")
    assert offset_pos == expected_offset, "Offset positioning failed"
    
    print("\n" + "=" * 50)
    print("✅ All zone grid tests passed!")
    print(f"✅ Successfully created {len(all_zones)} zones with complete ice coverage")
    print("✅ Zone positioning, lookup, and adjacency systems working correctly")
    
    return True

if __name__ == "__main__":
    try:
        test_zone_grid()
        print("\n🎉 Zone Grid implementation is ready for use!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)