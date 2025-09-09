#!/usr/bin/env python3
"""
Direct test of the hockey diagram agent without MCP.
"""
import asyncio
import os
import sys
import json
from datetime import datetime

# Set API key
os.environ['OPENAI_API_KEY'] = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('OPENAI_API_KEY', '')

from hockey_diagram_agent import get_agent

async def test_diagrams():
    """Test various diagram types."""
    print("🧪 Hockey Diagram Agent - Direct Testing")
    print("=" * 60)
    
    # Initialize agent
    print("\n🤖 Initializing agent...")
    agent = await get_agent()
    print("✅ Agent initialized")
    
    # Test cases
    test_cases = [
        {
            "name": "Simple Formation - 2-1-2 Forecheck",
            "request": "2-1-2 forecheck",
            "expected_tools": ["parse_hockey_formation", "generate_diagram_from_spec"]
        },
        {
            "name": "Complex System - Power Play Umbrella",
            "request": "power play umbrella formation with movement from half-wall",
            "expected_tools": ["parse_hockey_formation", "generate_diagram_from_spec"]
        },
        {
            "name": "Unknown Formation - Swedish Torpedo",
            "request": "Swedish torpedo forecheck",
            "expected_tools": ["search_hockey_tactics", "generate_hockey_diagram"]
        },
        {
            "name": "Drill Description",
            "request": "passing drill with 3 players in triangle formation",
            "expected_tools": ["parse_hockey_formation", "generate_diagram_from_spec"]
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {test['name']}")
        print(f"Request: {test['request']}")
        print("-" * 40)
        
        try:
            start_time = datetime.now()
            result = await agent.generate_diagram(test['request'])
            end_time = datetime.now()
            
            # Print results
            print(f"\n✅ Success: {result.get('success', False)}")
            print(f"⏱️  Time: {result.get('processing_time', 0):.2f}s")
            
            # Print trace
            if 'trace' in result:
                trace = result['trace']
                print(f"\n📋 Trace:")
                print(f"   Steps: {trace.get('total_steps', 0)}")
                print(f"   Sequence: {trace.get('tools_sequence', 'N/A')}")
                
                # Detailed steps
                if 'steps' in trace:
                    print(f"\n   Detailed Steps:")
                    for j, step in enumerate(trace['steps'], 1):
                        print(f"   {j}. {step.get('name', 'Unknown')}")
                        if 'arguments' in step:
                            args_str = str(step['arguments'])[:100]
                            print(f"      Args: {args_str}...")
            
            # Print diagram path
            if result.get('diagram_path'):
                print(f"\n📁 Diagram: {result['diagram_path']}")
            
            # Extract key info
            results.append({
                "test": test['name'],
                "success": result.get('success', False),
                "time": result.get('processing_time', 0),
                "tools": result.get('tools_used', []),
                "diagram_path": result.get('diagram_path'),
                "trace": result.get('trace', {})
            })
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            results.append({
                "test": test['name'],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print("=" * 60)
    
    successful = sum(1 for r in results if r.get('success', False))
    print(f"\nTotal: {len(results)} tests")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {len(results) - successful}")
    
    print("\n📋 Detailed Results:")
    for r in results:
        status = "✅" if r.get('success', False) else "❌"
        print(f"\n{status} {r['test']}")
        if r.get('success'):
            print(f"   Time: {r.get('time', 0):.2f}s")
            print(f"   Tools: {' → '.join(r.get('tools', []))}")
            if r.get('diagram_path'):
                print(f"   Path: {r['diagram_path']}")
        else:
            print(f"   Error: {r.get('error', 'Unknown')}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2 and not os.environ.get('OPENAI_API_KEY'):
        print("Usage: python test_direct_agent.py <OPENAI_API_KEY>")
        sys.exit(1)
    
    asyncio.run(test_diagrams())