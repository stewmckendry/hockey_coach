#!/usr/bin/env python3
"""
Test script for hockey diagram generation.
Tests the generator directly without MCP server.
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from servers.hockey_diagram_mcp.generator import HockeyDiagramGenerator, Player, Movement, Zone
from servers.hockey_diagram_mcp.parser import HockeyPromptParser
from servers.hockey_diagram_mcp.elements import FORMATIONS

async def test_basic_diagram():
    """Test basic diagram generation with a 2-1-2 forecheck."""
    print("Testing basic 2-1-2 forecheck diagram...")
    
    generator = HockeyDiagramGenerator()
    
    # Define players for 2-1-2 forecheck
    players = [
        Player(position="LW", x=60, y=-20, team="home"),
        Player(position="RW", x=60, y=20, team="home"),
        Player(position="C", x=40, y=0, team="home"),
        Player(position="LD", x=10, y=-15, team="home"),
        Player(position="RD", x=10, y=15, team="home"),
        Player(position="G", x=-89, y=0, team="home"),
        # Opposing team
        Player(position="X1", x=85, y=0, team="away", has_puck=True),
        Player(position="X2", x=70, y=-20, team="away"),
        Player(position="X3", x=70, y=20, team="away"),
    ]
    
    # Define movements
    movements = [
        Movement(from_position="LW", to_position=(80, -15), movement_type="forecheck"),
        Movement(from_position="RW", to_position=(80, 15), movement_type="forecheck"),
        Movement(from_position="C", to_position=(50, 0), movement_type="skating"),
    ]
    
    # Generate diagram
    base64_image = generator.generate_diagram(
        players=players,
        movements=movements,
        title="2-1-2 Forecheck Test",
        view="full"
    )
    
    # Save to file
    output_path = "test_2-1-2_forecheck.png"
    generator.save_to_file(base64_image, output_path)
    print(f"✅ Saved diagram to: {output_path}")
    
    return True

async def test_parser():
    """Test the natural language parser."""
    print("\nTesting natural language parser...")
    
    parser = HockeyPromptParser()
    
    # Test prompts
    prompts = [
        "Create a 2-1-2 forecheck with F1 pressuring behind the net",
        "Show power play umbrella formation",
        "Draw defensive zone coverage with box formation"
    ]
    
    for prompt in prompts:
        print(f"\nParsing: '{prompt}'")
        try:
            spec = await parser.parse_prompt(prompt)
            print(f"  Players: {len(spec.players)}")
            print(f"  Movements: {len(spec.movements or [])}")
            print(f"  Title: {spec.title}")
        except Exception as e:
            print(f"  Error: {e}")
    
    return True

async def test_zone_view():
    """Test different zone views."""
    print("\nTesting zone views...")
    
    generator = HockeyDiagramGenerator()
    
    # Offensive zone setup
    players = [
        Player(position="C", x=65, y=0, team="home"),
        Player(position="LW", x=85, y=-25, team="home", has_puck=True),
        Player(position="RW", x=70, y=25, team="home"),
        Player(position="LD", x=30, y=-20, team="home"),
        Player(position="RD", x=30, y=20, team="home"),
        Player(position="G", x=-89, y=0, team="home"),
    ]
    
    # Test different views
    views = ["full", "offensive", "defensive", "neutral"]
    
    for view in views:
        base64_image = generator.generate_diagram(
            players=players,
            title=f"Test - {view.capitalize()} Zone View",
            view=view
        )
        
        output_path = f"test_view_{view}.png"
        generator.save_to_file(base64_image, output_path)
        print(f"✅ Saved {view} view to: {output_path}")
    
    return True

async def test_preset_formation():
    """Test using a preset formation."""
    print("\nTesting preset formations...")
    
    generator = HockeyDiagramGenerator()
    parser = HockeyPromptParser()
    
    # Get a preset formation
    formation_data = FORMATIONS["1-3-1_powerplay"]
    
    # Convert to Player objects
    players = [
        Player(**p) for p in formation_data["players"]
    ]
    
    # Add opposing team
    players.extend([
        Player(position="X1", x=-50, y=-10, team="away"),
        Player(position="X2", x=-50, y=10, team="away"),
        Player(position="X3", x=-70, y=-10, team="away"),
        Player(position="X4", x=-70, y=10, team="away"),
    ])
    
    # Generate diagram
    base64_image = generator.generate_diagram(
        players=players,
        title="1-3-1 Power Play Formation",
        view="full"
    )
    
    output_path = "test_powerplay_formation.png"
    generator.save_to_file(base64_image, output_path)
    print(f"✅ Saved power play formation to: {output_path}")
    
    return True

async def main():
    """Run all tests."""
    print("🏒 Hockey Diagram Generator Test Suite")
    print("=" * 50)
    
    tests = [
        test_basic_diagram,
        test_parser,
        test_zone_view,
        test_preset_formation
    ]
    
    for test in tests:
        try:
            await test()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n✅ All tests completed!")
    print("Check the generated PNG files to verify diagram quality.")

if __name__ == "__main__":
    asyncio.run(main())