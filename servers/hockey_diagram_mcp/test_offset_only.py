#!/usr/bin/env python3
"""
Simple test script for the enhanced offset system.
Tests without dependencies on MCP or OpenAI.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from offset_system import parse_offset, get_offset_description, offset_system


def test_offset_system():
    """Test the enhanced offset system."""
    print("🧪 Testing Enhanced Offset System...")
    print("=" * 50)
    
    # Test basic descriptive offsets
    print("\n📍 Basic Offset Tests:")
    test_cases = [
        ("deep", "defensive"),
        ("high", "offensive"),
        ("near_boards", "neutral"),
        ("slot_side", "offensive"),
        ("behind_net", "defensive"),
        ("point_left", "offensive"),
        ("corner_deep", "offensive"),
        ("faceoff", "neutral"),
        ("support_high", "defensive"),
    ]
    
    for description, zone_type in test_cases:
        offset_x, offset_y = parse_offset(description, zone_type)
        desc = get_offset_description(description, zone_type)
        print(f"  '{description:12}' in {zone_type:9} zone: ({offset_x:+5.1f}, {offset_y:+5.1f}) - {desc}")
    
    # Test compound descriptions
    print("\n📍 Compound Description Tests:")
    compound_tests = [
        ("deep near boards", "defensive"),
        ("high slot", "offensive"),
        ("shallow support", "neutral"),
        ("corner deep", "offensive"),
    ]
    
    for description, zone_type in compound_tests:
        offset_x, offset_y = parse_offset(description, zone_type)
        desc = get_offset_description(description, zone_type)
        print(f"  '{description:15}' in {zone_type:9} zone: ({offset_x:+5.1f}, {offset_y:+5.1f}) - {desc}")
    
    # Test dictionary format
    print("\n📍 Dictionary Format Tests:")
    dict_tests = [
        {"x": 5, "y": -8, "description": "custom position"},
        {"x": -3, "y": 12},
        {"description": "deep near boards"},
    ]
    
    for i, dict_offset in enumerate(dict_tests):
        offset_x, offset_y = parse_offset(dict_offset)
        print(f"  Dict {i+1:2d}: {str(dict_offset):40} -> ({offset_x:+5.1f}, {offset_y:+5.1f})")
    
    # Test available offsets
    print(f"\n📋 Available Offset Descriptors: {len(offset_system.DESCRIPTIVE_OFFSETS)}")
    
    # Show some popular ones
    popular_offsets = ["deep", "shallow", "high", "low", "slot", "corner", "point", "boards"]
    for offset_name in popular_offsets:
        if offset_name in offset_system.DESCRIPTIVE_OFFSETS:
            spec = offset_system.DESCRIPTIVE_OFFSETS[offset_name]
            print(f"  {offset_name:8}: ({spec.x:+4.0f}, {spec.y:+4.0f}) - {spec.description}")
    
    # Test validation
    print("\n🔒 Coordinate Validation Tests:")
    validation_tests = [
        (100, 50),    # Should be clamped
        (-30, -30),   # Should be clamped
        (5, -8),      # Should pass through
        (0, 0),       # Should pass through
    ]
    
    for test_x, test_y in validation_tests:
        valid_x, valid_y = offset_system.validate_offset_coordinates(test_x, test_y)
        clamped = "CLAMPED" if (valid_x != test_x or valid_y != test_y) else "OK"
        print(f"  ({test_x:+3.0f}, {test_y:+3.0f}) -> ({valid_x:+5.1f}, {valid_y:+5.1f}) {clamped}")
    
    print("\n✅ All offset system tests completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    test_offset_system()