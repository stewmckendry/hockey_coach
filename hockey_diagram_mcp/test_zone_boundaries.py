#!/usr/bin/env python3
"""Test the enhanced zone boundary system."""

import sys
import json
from src.zone_boundaries_enhanced import get_zone_boundaries_enhanced

def test_zone_queries():
    """Test various zone queries that were failing in the logs."""
    
    test_cases = [
        # Failed queries from logs
        ("full", "left_defensive_faceoff_dot", "Should find left defensive faceoff dot"),
        ("defensive", "left_defensive_faceoff_dot", "Should find in defensive view"),
        ("full", "blue_line", "Should interpret as defensive blue line"),
        ("defensive", "blue_line", "Should find blue line in defensive context"),
        ("defensive", "behind_net", "Should find behind net in defensive zone"),
        ("full", "backing up from the blue line", "Natural language for blue line"),
        
        # Point positions (were incorrectly at x=54)
        ("offensive", "left_point", "Should be at blue line x=25"),
        ("offensive", "right_point", "Should be at blue line x=25"),
        
        # Board variations
        ("full", "left boards", "Should find left boards"),
        ("full", "on the boards", "Natural language for boards"),
        ("offensive", "half-boards", "Should find half boards"),
        ("offensive", "left_half_boards", "Should find left half boards"),
        
        # Behind net variations
        ("defensive", "behind the net", "Natural language behind net"),
        ("offensive", "gretzky_office", "Alias for behind net"),
        
        # Center ice variations
        ("full", "center ice", "Natural language center"),
        ("neutral", "center_ice", "Direct center ice"),
        
        # Fuzzy matching tests
        ("full", "left_defensiv_faceoff", "Typo should fuzzy match"),
        ("offensive", "slt", "Should suggest 'slot'"),
        ("full", "blue lin", "Should match blue line"),
    ]
    
    print("=" * 80)
    print("TESTING ENHANCED ZONE BOUNDARY SYSTEM")
    print("=" * 80)
    
    for view, zone, description in test_cases:
        print(f"\n📍 Test: {description}")
        print(f"   Query: get_zone_boundaries_enhanced('{view}', '{zone}')")
        
        result = get_zone_boundaries_enhanced(view, zone)
        
        # Check if successful or has error
        if "error" in result:
            print(f"   ❌ ERROR: {result['error']}")
            if "suggestions" in result:
                print(f"   💡 Suggestions: {result['suggestions'][:3]}")
        else:
            print(f"   ✅ Found: {result['description']}")
            print(f"   📐 Center: x={result['center']['x']}, y={result['center']['y']}")
            
        if "interpreted_as" in result:
            print(f"   🔄 Interpreted as: {result['interpreted_as']}")
            
        if "warning" in result:
            print(f"   ⚠️  Warning: {result['warning']}")
    
    print("\n" + "=" * 80)
    print("SPECIFIC POSITION TESTS")
    print("=" * 80)
    
    # Test specific positions that were wrong
    critical_positions = [
        ("offensive", "left_point", 25, "Left point should be at blue line"),
        ("offensive", "right_point", 25, "Right point should be at blue line"),
        ("defensive", "behind_net", -92, "Behind net should be at x=-92"),
        ("offensive", "left_half_boards", 52, "Half boards between blue line and goal"),
    ]
    
    for view, zone, expected_x, description in critical_positions:
        result = get_zone_boundaries_enhanced(view, zone)
        actual_x = result['center']['x']
        status = "✅" if abs(actual_x - expected_x) < 5 else "❌"
        
        print(f"\n{status} {description}")
        print(f"   Expected x ≈ {expected_x}, Got x = {actual_x}")
        if abs(actual_x - expected_x) >= 5:
            print(f"   ⚠️  POSITION ERROR: Off by {abs(actual_x - expected_x)} units")


if __name__ == "__main__":
    test_zone_queries()