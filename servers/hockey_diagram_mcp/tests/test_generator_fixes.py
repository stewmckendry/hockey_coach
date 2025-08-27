#!/usr/bin/env python3
"""
Test script to verify generator fixes for Issue #97.

Tests:
1. Zone name mismatch fix (left_corner vs corner_left)
2. ZoneGrid integration for zone boundaries
3. Defensive positioning with zone-based coordinates

Run with: python test_generator_fixes.py
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generator import HockeyDiagramGenerator, Player, CoverageZone
from zone_grid import zone_grid
from coordinate_mapper import HockeyCoordinateMapper

def test_zone_name_mapping():
    """Test that parser zone names work correctly."""
    print("=== Testing Zone Name Mapping ===")
    
    generator = HockeyDiagramGenerator()
    
    # Test parser output zone names
    test_zones = ["left_corner", "right_corner", "defensive_left_corner", "defensive_right_corner"]
    
    for zone_name in test_zones:
        bounds = generator._get_zone_bounds(zone_name)
        if bounds:
            print(f"✓ {zone_name}: {bounds}")
        else:
            print(f"✗ {zone_name}: No bounds found")
    
    print()

def test_zone_grid_integration():
    """Test ZoneGrid integration."""
    print("=== Testing ZoneGrid Integration ===")
    
    generator = HockeyDiagramGenerator()
    
    # Test some ZoneGrid zone names
    test_zones = ["def-left-low", "off-center-left-mid-high", "neu-right-high"]
    
    for zone_name in test_zones:
        bounds = generator._get_zone_bounds(zone_name)
        if bounds:
            print(f"✓ {zone_name}: {bounds}")
        else:
            print(f"✗ {zone_name}: No bounds found")
    
    # Check zone coverage
    print(f"Total zones in grid: {len(zone_grid.zones)}")
    print(f"Zone distribution: {zone_grid.get_zone_area_distribution()}")
    print()

def test_defensive_positioning():
    """Test defensive positioning."""
    print("=== Testing Defensive Positioning ===")
    
    mapper = HockeyCoordinateMapper()
    
    # Test D1 and D2 positioning for box formation
    d1_coord = mapper.get_player_coordinate("LD", "defensive", role="box_defense")
    d2_coord = mapper.get_player_coordinate("RD", "defensive", role="box_defense") 
    
    print(f"D1 (LD) box position: {d1_coord}")
    print(f"D2 (RD) box position: {d2_coord}")
    
    # Check if they're positioned correctly (should be in front of net, not at face-off circles)
    # Face-off circles are at X: -69, goal line is at X: -89
    # Good box position should be between -70 and -50 (closer to net than circles)
    if d1_coord[0] > -70 and d2_coord[0] > -70:  # Closer to goal than face-off circles
        print("✓ Defensive positioning looks correct (closer to net than face-off circles)")
        print(f"  Box formation: D1 at {d1_coord}, D2 at {d2_coord}")
        print(f"  Reference: Face-off circles at X: -69, Goal line at X: -89")
    else:
        print("✗ Defensive positioning may need adjustment")
        print(f"  D1 X: {d1_coord[0]}, D2 X: {d2_coord[0]} (should be > -70)")
    
    print()

def test_zone_rendering():
    """Test zone rendering with CoverageZone."""
    print("=== Testing Zone Rendering ===")
    
    generator = HockeyDiagramGenerator()
    
    # Create test players
    players = [
        Player(position="C", x=0, y=0, team="home"),
        Player(position="LD", x=-80, y=-15, team="home"),
        Player(position="RD", x=-80, y=15, team="home"),
    ]
    
    # Create test coverage zones
    zones = [
        CoverageZone(zone_type="coverage", area="left_corner", team="home", opacity=0.2),
        CoverageZone(zone_type="pressure", area="def-center-left-low", team="home", opacity=0.3),
    ]
    
    try:
        # Generate diagram
        result = generator.generate_diagram(
            players=players,
            zones=zones,
            title="Test Zone Rendering",
            view="defensive"
        )
        
        if result and len(result) > 100:  # Basic check for base64 string
            print("✓ Zone rendering successful - diagram generated")
            print(f"  Base64 length: {len(result)} characters")
        else:
            print("✗ Zone rendering failed - no diagram generated")
    
    except Exception as e:
        print(f"✗ Zone rendering error: {e}")
    
    print()

def main():
    """Run all tests."""
    print("Testing Hockey Diagram Generator Fixes (Issue #97)")
    print("=" * 60)
    print()
    
    try:
        test_zone_name_mapping()
        test_zone_grid_integration()
        test_defensive_positioning()
        test_zone_rendering()
        
        print("=== Test Summary ===")
        print("All tests completed. Check results above for any failures.")
        
    except Exception as e:
        print(f"Test execution error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()