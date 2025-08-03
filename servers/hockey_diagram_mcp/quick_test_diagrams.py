#!/usr/bin/env python3
"""Quick test to generate a few sample diagrams."""

import asyncio
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

if len(sys.argv) > 1:
    os.environ['OPENAI_API_KEY'] = sys.argv[1]

from servers.hockey_diagram_mcp.server import generate_hockey_diagram

async def quick_test():
    """Generate a few quick test diagrams."""
    
    test_prompts = [
        ("2-1-2 forecheck", "offensive"),
        ("Box penalty kill", "defensive"),
        ("Power play umbrella", "offensive"),
        ("Triangle passing drill", "full")
    ]
    
    print("Quick Diagram Test\n" + "="*40)
    
    for prompt, view in test_prompts:
        print(f"\nGenerating: {prompt}")
        
        try:
            result = await generate_hockey_diagram(
                prompt=prompt,
                view=view
            )
            
            if result['success']:
                print(f"✅ Success! Saved to: {result['diagram_path']}")
                spec = result['diagram_spec']
                print(f"   Players: {len(spec['players'])}, Movements: {len(spec.get('movements', []))}")
            else:
                print(f"❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    if not os.environ.get('OPENAI_API_KEY'):
        print("Usage: python quick_test_diagrams.py [API_KEY]")
        sys.exit(1)
    
    asyncio.run(quick_test())