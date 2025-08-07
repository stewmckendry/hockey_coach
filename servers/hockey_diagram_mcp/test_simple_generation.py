#!/usr/bin/env python3
"""
Test simple diagram generation without agent.
"""
import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from two_stage_parser import TwoStageHockeyParser
from generator import HockeyDiagramGenerator

async def test_simple_generation():
    """Test basic diagram generation without agent."""
    print("🧪 Testing Simple Diagram Generation")
    print("=" * 60)
    
    test_cases = [
        "2-1-2 forecheck",
        "power play umbrella",
        "defensive zone coverage",
        "passing drill with 3 players"
    ]
    
    parser = TwoStageHockeyParser()
    generator = HockeyDiagramGenerator()
    
    for i, prompt in enumerate(test_cases, 1):
        print(f"\nTest {i}: {prompt}")
        print("-" * 40)
        
        try:
            # Parse
            start_time = datetime.now()
            spec = await parser.parse_prompt(prompt)
            parse_time = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ Parsed in {parse_time:.2f}s")
            print(f"   Type: {spec.diagram_type}")
            print(f"   Players: {len(spec.players)}")
            print(f"   View: {spec.view}")
            if spec.movements:
                print(f"   Movements: {len(spec.movements)}")
            if spec.zones:
                print(f"   Zones: {len(spec.zones)}")
            
            # Generate
            start_time = datetime.now()
            result = generator.generate_from_spec(spec)
            gen_time = (datetime.now() - start_time).total_seconds()
            
            if result['success']:
                print(f"✅ Generated in {gen_time:.2f}s")
                print(f"📁 File: {result['filename']}")
                print(f"   Size: {len(result['base64_data'])} chars (base64)")
            else:
                print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_simple_generation())