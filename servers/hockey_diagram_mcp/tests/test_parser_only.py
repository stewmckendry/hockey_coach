#!/usr/bin/env python3
"""
Test the two-stage parser in isolation without the full MCP server.
This helps debug parser issues separately from server integration.
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Set API key
if len(sys.argv) > 1:
    os.environ['OPENAI_API_KEY'] = sys.argv[1]

from servers.hockey_diagram_mcp.two_stage_parser import TwoStageHockeyParser

async def test_parser():
    """Test the two-stage parser directly."""
    
    if not os.environ.get('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not set!")
        print("Usage: python test_parser_only.py [API_KEY]")
        return
    
    # Initialize parser
    parser = TwoStageHockeyParser()
    
    # Test prompts
    prompts = [
        "2-1-2 forecheck with F1 pressuring behind net",
        "Pass from center to left wing in slot",
        "Box penalty kill formation"
    ]
    
    print("Testing Two-Stage Parser Directly\n" + "="*50)
    
    for prompt in prompts:
        print(f"\nTesting: '{prompt}'")
        print("-" * 40)
        
        try:
            # Parse the prompt
            result = await parser.parse_prompt(prompt)
            
            print(f"✅ Parse successful!")
            print(f"Diagram type: {result.diagram_type}")
            print(f"Title: {result.title}")
            print(f"View: {result.view}")
            print(f"Players: {len(result.players)}")
            
            # Show player details
            for i, player in enumerate(result.players):
                print(f"  Player {i+1}: {player.position} at ({player.x}, {player.y}) - Team: {player.team}")
            
            if result.movements:
                print(f"Movements: {len(result.movements)}")
                for i, movement in enumerate(result.movements):
                    print(f"  Movement {i+1}: {movement.from_position} → {movement.to_position} ({movement.movement_type})")
            
            if result.zones:
                print(f"Zones: {len(result.zones)}")
                for i, zone in enumerate(result.zones):
                    print(f"  Zone {i+1}: {zone.zone_type} - {zone.area}")
                    
        except Exception as e:
            print(f"❌ Parse failed: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """Run parser tests."""
    asyncio.run(test_parser())

if __name__ == "__main__":
    main()