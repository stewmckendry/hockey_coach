#!/usr/bin/env python3
"""Test the position mapping directly."""

import sys
import os
import json
from pathlib import Path

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'servers'))

from hockey_diagram_mcp_v3 import map_positions_with_llm

def test_position_mapping():
    """Test position mapping with LLM."""
    
    # Test players
    players = [
        {
            "id": "FW1",
            "type": "forward",
            "position_desc": "Offensive Forward 1 starting at the neutral zone dot"
        },
        {
            "id": "FW2", 
            "type": "forward",
            "position_desc": "Offensive Forward 2 starting at the neutral zone dot"
        },
        {
            "id": "D",
            "type": "defense",
            "position_desc": "Defenseman positioned at center ice"
        },
        {
            "id": "G",
            "type": "goalie",
            "position_desc": "Goalie in net"
        }
    ]
    
    print("=" * 70)
    print("TESTING POSITION MAPPING")
    print("=" * 70)
    
    # Test with different views
    for view in ["full", "neutral", "offensive"]:
        print(f"\n📍 Testing with view: {view}")
        print("-" * 50)
        
        result = map_positions_with_llm(players, view)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            continue
        
        if "players_mapped" in result:
            for player in result["players_mapped"]:
                coords = player.get("coordinates", {})
                print(f"\n{player['id']:5} → ({coords.get('x', 'N/A'):6.1f}, {coords.get('y', 'N/A'):6.1f})")
                print(f"      Zone: {player.get('zone', 'N/A')}")
                print(f"      Area: {player.get('area', 'N/A')}")
                print(f"      Confidence: {player.get('confidence', 0):.2f}")
                if player.get('reasoning'):
                    print(f"      Reasoning: {player['reasoning'][:100]}...")
        
        # Show any questions
        if "questions_for_user" in result and result["questions_for_user"]:
            print("\n❓ Questions:")
            for q in result["questions_for_user"]:
                print(f"  - {q['question']}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Set logging to DEBUG
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set in environment")
        sys.exit(1)
    
    test_position_mapping()