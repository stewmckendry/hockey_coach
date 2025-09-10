#!/usr/bin/env python3
"""
Quick test to confirm defensive coordinate mapping issue.
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from two_stage_parser import TwoStageHockeyParser

async def test_defensive_coordinates():
    """Test that defensive formations use negative X coordinates."""
    
    print("Testing defensive coordinate mapping...")
    print("="*50)
    
    # Get API key from command line or environment
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("Error: Need OPENAI_API_KEY as argument or environment variable")
        print("Usage: python test_defensive_coordinates.py [API_KEY]")
        return
    
    parser = TwoStageHockeyParser(api_key)
    
    # Test cases that should generate negative X coordinates
    test_cases = [
        ("defensive zone box formation for penalty kill", "defensive"),
        ("defensive zone coverage with D-to-D behind net", "defensive"),
        ("box penalty kill formation", "defensive"),
        ("diamond penalty kill in defensive zone", "defensive"),
    ]
    
    for prompt, view in test_cases:
        print(f"\nTesting: '{prompt}' with view '{view}'")
        print("-" * 40)
        
        try:
            context = {"diagram_type": "formation", "requested_view": view}
            diagram_spec = await parser.parse_prompt(prompt, context)
            
            print(f"Generated view: {diagram_spec.view}")
            print(f"Player positions:")
            
            issue_found = False
            for player in diagram_spec.players:
                print(f"  {player.position}: ({player.x:.1f}, {player.y:.1f}) - Team: {player.team}")
                
                # Check if defensive view but positive X coordinate
                if view == "defensive" and player.x > -25:
                    print(f"    ❌ ISSUE: Player at positive X coordinate in defensive view!")
                    issue_found = True
                elif view == "defensive" and player.x <= -25:
                    print(f"    ✅ Correct: Player in defensive zone (negative X)")
            
            if not issue_found and view == "defensive":
                print("  ✅ All players correctly positioned in defensive zone")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_defensive_coordinates())