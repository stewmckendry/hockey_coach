#!/usr/bin/env python3
"""
Test script for two-stage parser integration in the MCP server.
Tests that the server correctly uses the two-stage parser for diagram generation.
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Set API key from environment or command line
if len(sys.argv) > 1:
    os.environ['OPENAI_API_KEY'] = sys.argv[1]

from servers.hockey_diagram_mcp.server import generate_hockey_diagram, two_stage_parser

async def test_two_stage_integration():
    """Test the two-stage parser integration with various prompts."""
    
    test_cases = [
        {
            "prompt": "2-1-2 forecheck with F1 pressuring behind net",
            "expected_type": "formation",
            "expected_players": 5,
            "description": "Basic forecheck formation"
        },
        {
            "prompt": "Pass from center to left wing in slot",
            "expected_type": "drill",
            "expected_players": 2,
            "description": "Simple passing drill"
        },
        {
            "prompt": "Box penalty kill formation in defensive zone",
            "expected_type": "formation",
            "expected_players": 5,
            "description": "Penalty kill system"
        },
        {
            "prompt": "Power play umbrella with movement from half-wall to slot",
            "expected_type": "formation",
            "expected_players": 5,
            "description": "Power play with movement"
        }
    ]
    
    print("Testing Two-Stage Parser Integration\n" + "="*50)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Prompt: '{test['prompt']}'")
        
        try:
            # Test the MCP tool directly
            result = await generate_hockey_diagram(
                prompt=test['prompt'],
                diagram_type="tactical",
                view="full",
                output_format="png"
            )
            
            if result.get('success'):
                print(f"✅ Success! Generated diagram saved to: {result.get('diagram_path')}")
                
                # Check diagram spec
                spec = result.get('diagram_spec', {})
                if spec:
                    num_players = len(spec.get('players', []))
                    diagram_type = spec.get('diagram_type', 'unknown')
                    
                    print(f"   - Diagram type: {diagram_type}")
                    print(f"   - Players: {num_players}")
                    print(f"   - Has movements: {len(spec.get('movements', [])) > 0}")
                    print(f"   - Parser used: Check logs above")
                    
                    # Validate expectations
                    if diagram_type == test['expected_type']:
                        print(f"   ✓ Correct diagram type")
                    else:
                        print(f"   ✗ Expected type '{test['expected_type']}', got '{diagram_type}'")
                    
                    if num_players == test['expected_players']:
                        print(f"   ✓ Correct number of players")
                    else:
                        print(f"   ✗ Expected {test['expected_players']} players, got {num_players}")
                
                passed += 1
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed} passed, {failed} failed")
    
    # Test parser definitions
    print(f"\n{'='*50}")
    print("Testing Parser Definitions Access")
    try:
        definitions = two_stage_parser.get_definitions()
        print(f"✅ Parser has {len(definitions)} definition categories:")
        for category in definitions:
            print(f"   - {category}: {len(definitions[category])} items")
    except Exception as e:
        print(f"❌ Failed to get definitions: {e}")
    
    return passed, failed

def main():
    """Run the integration tests."""
    if not os.environ.get('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not set!")
        print("Usage: python test_two_stage_integration.py [API_KEY]")
        print("   or: export OPENAI_API_KEY=your_key")
        sys.exit(1)
    
    print(f"API Key configured: {'*' * 20}")
    
    # Run async tests
    passed, failed = asyncio.run(test_two_stage_integration())
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()