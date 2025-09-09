#!/usr/bin/env python3
"""
Validation test for the 4 specific fixes implemented:
1. Player overlap fix (team separation)
2. View filtering fix 
3. Movement validation fix
4. Zone opacity fix
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from servers.hockey_diagram_mcp.two_stage_parser import TwoStageHockeyParser, DiagramSpec
from servers.hockey_diagram_mcp.generator import HockeyDiagramGenerator, Player, Zone
from servers.hockey_diagram_mcp.server import _filter_players_by_view

async def test_player_overlap_fix():
    """Test Fix 1: Team separation logic"""
    print("\n1. Testing Player Overlap Fix...")
    
    # Create a parser instance
    parser = TwoStageHockeyParser()
    
    # Mock data with overlapping players
    data = {
        "players": [
            {"position": "C", "x": 0, "y": 0, "team": "home"},
            {"position": "X1", "x": 0, "y": 0, "team": "away"}  # Same position as home center
        ],
        "movements": [],
        "zones": []
    }
    
    # Mock structure analysis
    class MockStructure:
        diagram_category = "formation"
        primary_focus = "test"
    
    structure = MockStructure()
    
    # Apply validation which includes team separation
    result = parser._validate_and_correct(data, structure)
    
    # Check if away team player was moved
    home_center = next(p for p in result["players"] if p["position"] == "C")
    away_center = next(p for p in result["players"] if p["position"] == "X1")
    
    if home_center["x"] != away_center["x"]:
        print("✅ Team separation working - away player moved from overlapping position")
        return True
    else:
        print("❌ Team separation failed - players still overlap")
        return False

def test_view_filtering_fix():
    """Test Fix 2: View filtering logic"""
    print("\n2. Testing View Filtering Fix...")
    
    # Create mock diagram spec with players in different zones
    from servers.hockey_diagram_mcp.two_stage_parser import PlayerPosition
    
    players = [
        PlayerPosition(position="G", x=-89, y=0, team="home"),      # Goalie in defensive zone
        PlayerPosition(position="C", x=50, y=0, team="home"),      # Center in offensive zone
        PlayerPosition(position="RW", x=70, y=20, team="home"),    # Right wing in offensive zone
    ]
    
    # Create mock diagram spec
    class MockDiagramSpec:
        def __init__(self):
            self.players = players
            self.movements = []
            self.zones = []
    
    spec = MockDiagramSpec()
    
    # Test offensive zone filtering (should remove goalie)
    filtered_spec = _filter_players_by_view(spec, "offensive")
    
    goalie_filtered = not any(p.position == "G" for p in filtered_spec.players)
    offensive_players_kept = any(p.position in ["C", "RW"] for p in filtered_spec.players)
    
    if goalie_filtered and offensive_players_kept:
        print("✅ View filtering working - goalie removed from offensive view, forwards kept")
        return True
    else:
        print("❌ View filtering failed")
        return False

def test_movement_validation_fix():
    """Test Fix 3: Movement validation logic"""
    print("\n3. Testing Movement Validation Fix...")
    
    parser = TwoStageHockeyParser()
    
    # Test redundant movement (player moving to same position)
    player_positions = {"C": (0, 0), "RW": (20, 20)}
    
    # Movement to same position (should be invalid)
    redundant_movement = {
        "from_position": "C",
        "to_position": [0, 0],  # Same as current position
        "movement_type": "skating"
    }
    
    # Movement to different position (should be valid)
    valid_movement = {
        "from_position": "C", 
        "to_position": [10, 10],  # Different from current position
        "movement_type": "skating"
    }
    
    redundant_valid = parser._is_valid_movement(redundant_movement, player_positions)
    different_valid = parser._is_valid_movement(valid_movement, player_positions)
    
    if not redundant_valid and different_valid:
        print("✅ Movement validation working - redundant movements filtered, valid movements kept")
        return True
    else:
        print("❌ Movement validation failed")
        return False

def test_zone_opacity_fix():
    """Test Fix 4: Zone opacity is set to 0.2"""
    print("\n4. Testing Zone Opacity Fix...")
    
    # Test ZoneSpec default opacity
    from servers.hockey_diagram_mcp.two_stage_parser import ZoneSpec
    
    zone = ZoneSpec(
        zone_type="coverage",
        area="slot", 
        team="home"
    )
    
    # Test Zone dataclass default opacity
    from servers.hockey_diagram_mcp.generator import Zone
    
    generator_zone = Zone(
        zone_type="coverage",
        area="slot",
        team="home"
    )
    
    if zone.opacity == 0.2 and generator_zone.opacity == 0.2:
        print("✅ Zone opacity fix working - default opacity is 0.2")
        return True
    else:
        print(f"❌ Zone opacity failed - ZoneSpec: {zone.opacity}, Zone: {generator_zone.opacity}")
        return False

async def run_validation_tests():
    """Run all validation tests"""
    print("Hockey Diagram MCP Server - Fix Validation Tests")
    print("=" * 55)
    
    results = []
    
    # Test each fix
    results.append(await test_player_overlap_fix())
    results.append(test_view_filtering_fix())
    results.append(test_movement_validation_fix())
    results.append(test_zone_opacity_fix())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n{'='*55}")
    print(f"VALIDATION RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All fixes validated successfully!")
    else:
        print("⚠️  Some fixes need attention")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(run_validation_tests())