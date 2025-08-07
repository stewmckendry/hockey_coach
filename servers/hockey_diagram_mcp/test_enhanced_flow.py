#!/usr/bin/env python3
"""
Test script for the enhanced hockey diagram agent flow.

Tests the new synthesize_research_to_formation and map_formation_to_zones tools
along with the enhanced offset system.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from server import (
    synthesize_research_to_formation,
    map_formation_to_zones,
    generate_diagram_from_spec
)
from offset_system import parse_offset, get_offset_description


async def test_offset_system():
    """Test the enhanced offset system."""
    print("🧪 Testing Enhanced Offset System...")
    
    # Test basic descriptive offsets
    test_cases = [
        ("deep", "defensive"),
        ("high", "offensive"),
        ("near boards", "neutral"),
        ("slot side", "offensive"),
        ("behind net", "defensive"),
        ("point left", "offensive"),
        ("corner deep", "offensive"),
    ]
    
    for description, zone_type in test_cases:
        offset_x, offset_y = parse_offset(description, zone_type)
        desc = get_offset_description(description, zone_type)
        print(f"  📍 '{description}' in {zone_type} zone: ({offset_x:+.1f}, {offset_y:+.1f}) - {desc}")
    
    # Test dictionary format
    dict_offset = {"x": 5, "y": -8, "description": "custom position"}
    offset_x, offset_y = parse_offset(dict_offset)
    print(f"  📍 Dictionary offset: ({offset_x:+.1f}, {offset_y:+.1f})")
    
    print("✅ Offset system tests completed\n")


async def test_synthesis_tool():
    """Test the synthesize_research_to_formation tool."""
    print("🧪 Testing Research Synthesis Tool...")
    
    # Mock research results
    mock_research = [
        {
            "source": "Hockey Tactics Database",
            "content": "The Swedish torpedo system involves two forwards attacking in parallel lanes with high speed and coordination. F1 and F2 create intense pressure while F3 provides support from the high slot."
        },
        {
            "source": "European Hockey Systems",
            "content": "Swedish torpedo requires excellent conditioning. The two forecheckers must maintain parallel pressure while the third forward covers escape routes. Defense stays tight to blue line."
        }
    ]
    
    result = await synthesize_research_to_formation(mock_research, "Swedish torpedo forecheck")
    
    if result["success"]:
        formation_data = result["formation_data"]
        print(f"  ✅ Formation synthesized: {formation_data['name']}")
        print(f"  📋 Players: {', '.join(formation_data['players_involved'])}")
        print(f"  🎯 Primary zone: {formation_data['primary_zone']}")
        print(f"  📝 Steps: {len(formation_data['steps'])}")
        print(f"  💡 Hint: {formation_data['hint']}")
    else:
        print(f"  ❌ Synthesis failed: {result['error']}")
        return None
    
    print("✅ Synthesis tool test completed\n")
    return formation_data


async def test_zone_mapping_tool(formation_data):
    """Test the map_formation_to_zones tool."""
    print("🧪 Testing Zone Mapping Tool...")
    
    if not formation_data:
        print("  ⏭️  Skipping zone mapping - no formation data")
        return None
    
    result = await map_formation_to_zones(formation_data, include_movements=True, include_coverage=True)
    
    if result["success"]:
        diagram_spec = result["diagram_spec"]
        print(f"  ✅ Zone mapping completed")
        print(f"  👥 Players mapped: {result['player_count']}")
        print(f"  ➡️  Movements: {result['movement_count']}")
        print(f"  🎯 Coverage zones: {result['zone_count']}")
        print(f"  💡 Hint: {diagram_spec['hint']}")
        
        # Show sample player mapping
        players = diagram_spec.get('players', [])
        if players:
            sample_player = players[0]
            print(f"  📍 Sample mapping: {sample_player.get('role', 'Unknown')} -> {sample_player.get('zone', 'Unknown')}")
            offset = sample_player.get('offset', {})
            if offset:
                print(f"      Offset: {offset}")
    else:
        print(f"  ❌ Zone mapping failed: {result['error']}")
        return None
    
    print("✅ Zone mapping tool test completed\n")
    return diagram_spec


async def test_diagram_generation(diagram_spec):
    """Test diagram generation from spec."""
    print("🧪 Testing Diagram Generation...")
    
    if not diagram_spec:
        print("  ⏭️  Skipping diagram generation - no diagram spec")
        return
    
    result = await generate_diagram_from_spec(diagram_spec, output_format="png")
    
    if result["success"]:
        print(f"  ✅ Diagram generated: {result['diagram_path']}")
        print(f"  ⏱️  Generation time: {result['generation_time']:.3f}s")
    else:
        print(f"  ❌ Diagram generation failed: {result.get('error', 'Unknown error')}")
    
    print("✅ Diagram generation test completed\n")


async def test_complete_flow():
    """Test the complete enhanced flow."""
    print("🚀 Testing Complete Enhanced Flow...")
    print("=" * 60)
    
    try:
        # Test each component
        await test_offset_system()
        
        # Test synthesis
        formation_data = await test_synthesis_tool()
        
        # Test zone mapping
        diagram_spec = await test_zone_mapping_tool(formation_data)
        
        # Test diagram generation
        await test_diagram_generation(diagram_spec)
        
        print("🎉 Enhanced flow test completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if we have OpenAI API key
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Skipping LLM-dependent tests.")
        print("Only testing offset system...")
        asyncio.run(test_offset_system())
    else:
        print("🔑 OpenAI API key found. Running full test suite...")
        asyncio.run(test_complete_flow())