#!/usr/bin/env python3
"""Test the new MCP resources."""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from servers.hockey_mcp import (
    get_drill_categories, get_drills_by_category,
    get_tactic_categories, get_tactics_by_category,
    get_video_categories, get_videos_by_category,
    get_dryland_categories, get_dryland_by_category
)

def test_drill_resources():
    """Test drill resources."""
    print("\n🏒 Testing Drill Resources...")
    
    # Test categories
    result = get_drill_categories()
    data = json.loads(result)
    print(f"  ✅ Found {len(data['categories'])} drill categories")
    if data['categories']:
        print(f"  Sample categories: {[c['category'] for c in data['categories'][:5]]}")
        
        # Test by-category
        test_category = data['categories'][0]['category']
        result = get_drills_by_category(test_category)
        drill_data = json.loads(result)
        print(f"  ✅ Found {drill_data['count']} drills for '{test_category}'")

def test_tactic_resources():
    """Test tactic resources."""
    print("\n🎯 Testing Tactic Resources...")
    
    # Test categories
    result = get_tactic_categories()
    data = json.loads(result)
    print(f"  ✅ Found {len(data['categories'])} tactic categories")
    if data['categories']:
        print(f"  Sample categories: {[c['category'] for c in data['categories'][:5]]}")
        
        # Test by-category
        test_category = data['categories'][0]['category']
        result = get_tactics_by_category(test_category)
        tactic_data = json.loads(result)
        print(f"  ✅ Found {tactic_data['count']} tactics for '{test_category}'")

def test_video_resources():
    """Test video resources."""
    print("\n📹 Testing Video Resources...")
    
    # Test categories
    result = get_video_categories()
    data = json.loads(result)
    print(f"  ✅ Found {len(data['categories'])} video categories")
    if data['categories']:
        print(f"  Sample categories: {[c['category'] for c in data['categories'][:5]]}")
        
        # Test by-category
        test_category = data['categories'][0]['category']
        result = get_videos_by_category(test_category)
        video_data = json.loads(result)
        print(f"  ✅ Found {video_data['count']} videos for '{test_category}'")

def test_dryland_resources():
    """Test dryland resources."""
    print("\n💪 Testing Dryland Resources...")
    
    # Test categories
    result = get_dryland_categories()
    data = json.loads(result)
    print(f"  ✅ Found {len(data['categories'])} dryland categories")
    if data['categories']:
        print(f"  Sample categories: {[c['category'] for c in data['categories'][:5]]}")
        
        # Test by-category
        test_category = data['categories'][0]['category']
        result = get_dryland_by_category(test_category)
        dryland_data = json.loads(result)
        print(f"  ✅ Found {dryland_data['count']} exercises for '{test_category}'")

if __name__ == "__main__":
    print("🏒 Testing New Hockey MCP Resources\n")
    print("=" * 50)
    
    test_drill_resources()
    test_tactic_resources()
    test_video_resources()
    test_dryland_resources()
    
    print("\n" + "=" * 50)
    print("✅ All resource tests completed!")