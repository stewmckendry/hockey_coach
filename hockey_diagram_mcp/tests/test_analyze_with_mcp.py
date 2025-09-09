#!/usr/bin/env python3
"""Test analyze_hockey_query with MCP enabled."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from servers.hockey_diagram_mcp_v3 import analyze_hockey_query

def test_analyze_with_mcp():
    """Test the analyze tool with MCP enabled for web search."""
    
    print("=" * 80)
    print("Testing: Analyze with MCP Web Search")
    print("=" * 80)
    
    # Query that might benefit from web search
    query = "Power play setup with umbrella formation"
    
    print(f"\n1. Analyzing query: {query}")
    print("   Using Exa MCP for enhanced hockey knowledge...")
    
    # Analyze with MCP enabled (will use Exa if API key is available)
    result = analyze_hockey_query(query, use_exa_mcp=True)
    
    if result.get("error"):
        print(f"\n❌ Analysis failed: {result.get('error')}")
        if result.get("debug"):
            print("\nDebug info:")
            print(json.dumps(result.get("debug"), indent=2))
        return None
    
    print(f"\n✅ Analysis successful!")
    print(f"   API used: {result.get('api_used', 'unknown')}")
    print(f"   MCP tools called: {len(result.get('mcp_calls', []))}")
    
    # Show components
    components = result.get("components_with_assumptions", {})
    print(f"\n2. Components extracted:")
    print(f"   Players: {len(components.get('players', []))}")
    print(f"   Movements: {len(components.get('movements', []))}")
    print(f"   Zones: {len(components.get('zones', []))}")
    print(f"   Annotations: {len(components.get('annotations', []))}")
    
    # Show player positions
    print("\n3. Player positions:")
    for player in components.get("players", []):
        print(f"   {player.get('id')}: {player.get('type')} - {player.get('position_desc')}")
    
    # Show any questions for user
    questions = result.get("questions_for_user", [])
    if questions:
        print(f"\n4. Questions for clarification: {len(questions)}")
        for i, q in enumerate(questions, 1):
            print(f"   {i}. {q.get('question')}")
    
    return result

if __name__ == "__main__":
    # Load environment variables for API keys
    from dotenv import load_dotenv
    load_dotenv()
    
    result = test_analyze_with_mcp()
    
    if result:
        print("\n" + "=" * 80)
        print("✅ Test complete! Analyze tool working with MCP.")
        print("=" * 80)