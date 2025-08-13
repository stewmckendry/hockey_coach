#!/usr/bin/env python3
"""
Test script for the Hockey Formation Parser Agent
"""

import asyncio
import sys
import os
import json
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/liammckendry/thunder_playbook_worktrees/issue-101/.env')

# Add the thunder_playbook and server paths
sys.path.append('/Users/liammckendry/thunder_playbook')
sys.path.append('/Users/liammckendry/thunder_playbook_worktrees/issue-101/servers/hockey_diagram_mcp')

try:
    from parser_agent import parse_with_agent
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure virtual environment is activated: source /Users/liammckendry/spacy_env/bin/activate")
    sys.exit(1)

# Test cases for parser agent
TEST_CASES = [
    {
        "name": "Standard NHL - 1-3-1 Power Play",
        "description": "1-3-1 power play formation",
        "expected_sources": ["hockey_mcp"],
        "expected_players": 5,
        "category": "standard"
    },
    {
        "name": "Standard NHL - 2-1-2 Forecheck", 
        "description": "2-1-2 forecheck system",
        "expected_sources": ["hockey_mcp"],
        "expected_players": 5,
        "category": "standard"
    },
    {
        "name": "International - Swedish Torpedo Forecheck",
        "description": "Swedish torpedo forecheck formation",
        "expected_sources": ["web_search_exa"],  # Should cascade to web search
        "expected_players": 5,
        "category": "international"
    },
    {
        "name": "International - Finnish Box+1",
        "description": "Finnish box+1 system",
        "expected_sources": ["hockey_mcp", "web_search_exa"],  # Might find partial, then cascade
        "expected_players": 5,
        "category": "international"
    },
    {
        "name": "Drill - 3v2 Continuous",
        "description": "3v2 continuous drill",
        "expected_sources": ["hockey_drills", "web_search_exa"],
        "expected_players": 5,
        "category": "drill"
    },
    {
        "name": "Modern - Stretch Pass Breakout",
        "description": "stretch pass breakout system",
        "expected_sources": ["hockey_mcp", "web_search_exa"],
        "expected_players": 5,
        "category": "modern"
    }
]

async def test_parser_agent():
    """Run comprehensive tests on the parser agent."""
    print("🏒 HOCKEY FORMATION PARSER AGENT TESTING")
    print("=" * 60)
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES):
        print(f"\n📋 Test {i+1}/{len(TEST_CASES)}: {test_case['name']}")
        print(f"Query: {test_case['description']}")
        print("-" * 40)
        
        try:
            # Call parser agent
            result_json = await parse_with_agent(test_case['description'])
            result_data = json.loads(result_json)
            
            # Extract test results
            test_result = {
                "test_name": test_case['name'],
                "query": test_case['description'],
                "category": test_case['category'],
                "success": result_data.get('success', False),
                "tools_used": result_data.get('tools_used', []),
                "spec_generated": bool(result_data.get('parsed_data')),
                "player_count": len(result_data.get('parsed_data', {}).get('players', [])) if result_data.get('success') else 0,
                "research_cascade": len(result_data.get('tools_used', [])) > 1,
                "error": result_data.get('error') if not result_data.get('success') else None
            }
            
            # Print results
            print(f"✅ Success: {test_result['success']}")
            print(f"🛠️  Tools Used: {' → '.join(test_result['tools_used'])}")
            print(f"👥 Players: {test_result['player_count']}")
            print(f"🔄 Cascade: {test_result['research_cascade']}")
            
            if test_result['success'] and result_data.get('parsed_data'):
                spec = result_data['parsed_data']
                print(f"📊 Spec: {spec.get('diagram_type')} - {spec.get('title')}")
                print(f"🎯 View: {spec.get('view')}")
                
                # Show first few player positions
                players = spec.get('players', [])[:3]
                for player in players:
                    print(f"   {player.get('position')} → {player.get('zone')}")
                if len(spec.get('players', [])) > 3:
                    print(f"   ... and {len(spec.get('players', [])) - 3} more players")
            
            if test_result['error']:
                print(f"❌ Error: {test_result['error']}")
                
            results.append(test_result)
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            results.append({
                "test_name": test_case['name'],
                "query": test_case['description'],
                "category": test_case['category'],
                "success": False,
                "error": str(e),
                "tools_used": [],
                "spec_generated": False,
                "player_count": 0,
                "research_cascade": False
            })
    
    # Summary analysis
    print("\n\n📊 TEST SUMMARY")
    print("=" * 60)
    
    success_rate = sum(1 for r in results if r['success']) / len(results) * 100
    cascade_rate = sum(1 for r in results if r['research_cascade']) / len(results) * 100
    
    print(f"Overall Success Rate: {success_rate:.1f}%")
    print(f"Research Cascade Rate: {cascade_rate:.1f}%")
    
    # Category breakdown
    categories = {}
    for result in results:
        cat = result['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'success': 0, 'cascade': 0}
        categories[cat]['total'] += 1
        if result['success']:
            categories[cat]['success'] += 1
        if result['research_cascade']:
            categories[cat]['cascade'] += 1
    
    print("\n📈 Category Performance:")
    for cat, stats in categories.items():
        success_pct = stats['success'] / stats['total'] * 100
        cascade_pct = stats['cascade'] / stats['total'] * 100
        print(f"  {cat.title()}: {success_pct:.1f}% success, {cascade_pct:.1f}% cascade")
    
    # Tool usage analysis
    all_tools = []
    for result in results:
        all_tools.extend(result['tools_used'])
    
    from collections import Counter
    tool_counts = Counter(all_tools)
    
    print("\n🛠️ Tool Usage:")
    for tool, count in tool_counts.most_common():
        print(f"  {tool}: {count} times")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_parser_agent())