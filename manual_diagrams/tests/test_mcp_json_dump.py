#!/usr/bin/env python3
"""Dump full JSON response from analyze_hockey_query with MCP to verify field structure."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from servers.hockey_diagram_mcp_v3 import analyze_hockey_query
from pathlib import Path

def test_and_dump_json():
    """Test MCP-enhanced analysis and dump full JSON response."""
    
    print("=" * 80)
    print("Testing: MCP-Enhanced Analysis - Full JSON Dump")
    print("=" * 80)
    
    # Test multiple queries
    test_queries = [
        "Torpedo system neutral zone regroup",
        "Michigan move around the net",
        "Gretzky's office setup play",
        "1-3-1 power play formation"
    ]
    
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: {query}")
        print("-" * 60)
        
        # Analyze with MCP enabled
        result = analyze_hockey_query(query, use_exa_mcp=True)
        
        if result.get("error"):
            print(f"   ❌ Analysis failed: {result.get('error')}")
            continue
        
        # Save full JSON response
        output_file = output_dir / f"mcp_response_{i}_{query[:20].replace(' ', '_')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"   ✅ Saved to: {output_file.name}")
        
        # Print field structure analysis
        print("\n   Field Structure:")
        print(f"   - original_query: {'✓' if 'original_query' in result else '✗'}")
        print(f"   - explicit_info: {'✓' if 'explicit_info' in result else '✗'}")
        if 'explicit_info' in result:
            ei = result['explicit_info']
            print(f"     - situation: {ei.get('situation', 'MISSING')}")
            print(f"     - zone: {ei.get('zone', 'MISSING')}")
            print(f"     - key_actions: {len(ei.get('key_actions', []))} items")
            print(f"     - faceoff_location: {ei.get('faceoff_location', 'MISSING')}")
        
        print(f"   - components_with_assumptions: {'✓' if 'components_with_assumptions' in result else '✗'}")
        if 'components_with_assumptions' in result:
            comp = result['components_with_assumptions']
            print(f"     - rink: {'✓' if 'rink' in comp else '✗'}")
            print(f"     - players: {len(comp.get('players', []))} items")
            for j, player in enumerate(comp.get('players', [])[:3]):
                print(f"       Player {j+1}:")
                print(f"         - id: {player.get('id', 'MISSING')}")
                print(f"         - type: {player.get('type', 'MISSING')}")
                print(f"         - team: {player.get('team', 'MISSING')}")
                print(f"         - position_desc: {player.get('position_desc', 'MISSING')[:50]}...")
                print(f"         - to_player: {player.get('to_player', 'N/A (not a movement)')}")
            
            print(f"     - movements: {len(comp.get('movements', []))} items")
            for j, movement in enumerate(comp.get('movements', [])[:3]):
                print(f"       Movement {j+1}:")
                print(f"         - id: {movement.get('id', 'MISSING')}")
                print(f"         - type: {movement.get('type', 'MISSING')}")
                print(f"         - from_player: {movement.get('from_player', 'MISSING')}")
                print(f"         - to_player: {movement.get('to_player', 'N/A (not a pass)')}")
                print(f"         - to_area: {movement.get('to_area', 'MISSING')}")
            
            print(f"     - zones: {len(comp.get('zones', []))} items")
            print(f"     - annotations: {len(comp.get('annotations', []))} items")
            print(f"     - equipment: {len(comp.get('equipment', []))} items")
            print(f"     - coaches: {len(comp.get('coaches', []))} items (EXTRA FIELD)")
        
        print(f"   - questions_for_user: {len(result.get('questions_for_user', []))} items")
        print(f"   - metadata: {'✓' if 'metadata' in result else '✗'}")
        if 'metadata' in result:
            meta = result['metadata']
            print(f"     - type: {meta.get('type', 'MISSING')}")
            print(f"     - phase: {meta.get('phase', 'MISSING')}")
            print(f"     - key_players: {meta.get('key_players', [])}")
        
        # Check for extra fields from API response
        print(f"\n   API Response Fields:")
        print(f"   - api_used: {result.get('api_used', 'N/A')}")
        print(f"   - exa_available: {result.get('exa_available', 'N/A')}")
        print(f"   - mcp_calls: {len(result.get('mcp_calls', []))} calls")
        print(f"   - mcp_tools_configured: {result.get('mcp_tools_configured', [])}")
        print(f"   - response_id: {result.get('response_id', 'N/A')[:20]}..." if result.get('response_id') else "   - response_id: N/A")
        
        # Check for unexpected fields
        expected_fields = {
            'original_query', 'explicit_info', 'components_with_assumptions',
            'questions_for_user', 'metadata', 'api_used', 'exa_available',
            'mcp_calls', 'mcp_tools_configured', 'api_mode', 'response_id',
            'conversation'
        }
        unexpected = set(result.keys()) - expected_fields
        if unexpected:
            print(f"\n   ⚠️ UNEXPECTED FIELDS: {unexpected}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_and_dump_json()
    
    print("\n" + "=" * 80)
    print("✅ JSON dump complete! Check outputs/ directory for full responses.")
    print("=" * 80)