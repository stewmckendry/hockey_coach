#!/usr/bin/env python3
"""
Generate test diagrams for all major hockey formations and scenarios.
This validates the two-stage parser can handle various hockey concepts.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Set API key
if len(sys.argv) > 1:
    os.environ['OPENAI_API_KEY'] = sys.argv[1]

from servers.hockey_diagram_mcp.server import generate_hockey_diagram

# Test scenarios organized by category
TEST_SCENARIOS = {
    "Forechecking Systems": [
        ("2-1-2 forecheck with F1 behind net", "offensive"),
        ("1-2-2 forecheck with center pressure", "offensive"),
        ("2-3 forecheck aggressive pressure", "offensive"),
        ("1-3-1 neutral zone trap", "neutral"),
    ],
    
    "Power Play Formations": [
        ("1-3-1 power play umbrella", "offensive"),
        ("Power play overload left side", "offensive"),
        ("Power play spread formation", "offensive"),
        ("Power play with net front presence", "offensive"),
    ],
    
    "Penalty Kill Systems": [
        ("Box penalty kill formation", "defensive"),
        ("Diamond penalty kill", "defensive"),
        ("Aggressive penalty kill pressure", "defensive"),
        ("Penalty kill with rotation", "defensive"),
    ],
    
    "Defensive Zone Coverage": [
        ("Man-on-man defensive coverage", "defensive"),
        ("Zone defense in own end", "defensive"),
        ("Defensive zone faceoff setup", "defensive"),
        ("Collapsing defense around net", "defensive"),
    ],
    
    "Breakout Plays": [
        ("D-to-D breakout with center support", "defensive"),
        ("Quick up breakout", "full"),
        ("Reverse breakout behind net", "defensive"),
        ("Stretch pass breakout", "full"),
    ],
    
    "Offensive Zone Plays": [
        ("Cycle play in offensive zone", "offensive"),
        ("Behind the net play setup", "offensive"),
        ("High-low offensive play", "offensive"),
        ("Offensive zone faceoff play", "offensive"),
    ],
    
    "Drills": [
        ("3v2 rush drill from neutral zone", "full"),
        ("Triangle passing drill", "neutral"),
        ("2v1 defensive drill", "defensive"),
        ("Breakout drill with regroup", "full"),
        ("Power play entry drill", "neutral"),
        ("Shooting drill from slot", "offensive"),
    ],
    
    "Special Situations": [
        ("6v5 with goalie pulled", "offensive"),
        ("3v3 overtime formation", "full"),
        ("Delayed penalty setup", "offensive"),
        ("Empty net defensive formation", "defensive"),
    ]
}

async def generate_test_diagram(prompt, view, category, index):
    """Generate a single test diagram."""
    print(f"  [{index}] Generating: {prompt}")
    
    try:
        result = await generate_hockey_diagram(
            prompt=prompt,
            diagram_type="tactical",
            view=view,
            output_format="png"
        )
        
        if result.get('success'):
            path = result.get('diagram_path', 'Unknown')
            players = len(result.get('diagram_spec', {}).get('players', []))
            movements = len(result.get('diagram_spec', {}).get('movements', []))
            
            print(f"      ✅ Success! {players} players, {movements} movements")
            print(f"      📁 Saved to: {path}")
            return True, path
        else:
            print(f"      ❌ Failed: {result.get('error', 'Unknown error')}")
            return False, None
            
    except Exception as e:
        print(f"      ❌ Exception: {str(e)}")
        return False, None

async def generate_all_diagrams():
    """Generate all test diagrams."""
    print("Hockey Diagram Test Suite")
    print("=" * 60)
    print(f"Generating {sum(len(scenarios) for scenarios in TEST_SCENARIOS.values())} test diagrams")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    total = 0
    successful = 0
    failed = 0
    results = {}
    
    for category, scenarios in TEST_SCENARIOS.items():
        print(f"\n{category}")
        print("-" * len(category))
        
        category_results = []
        
        for i, (prompt, view) in enumerate(scenarios, 1):
            total += 1
            success, path = await generate_test_diagram(prompt, view, category, i)
            
            if success:
                successful += 1
                category_results.append({
                    "prompt": prompt,
                    "view": view,
                    "path": path,
                    "success": True
                })
            else:
                failed += 1
                category_results.append({
                    "prompt": prompt,
                    "view": view,
                    "success": False
                })
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        results[category] = category_results
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Total diagrams: {total}")
    print(f"Successful: {successful} ({successful/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save results summary
    summary_path = Path("servers/hockey_diagram_mcp/generated_diagrams/test_summary.txt")
    with open(summary_path, 'w') as f:
        f.write(f"Hockey Diagram Test Results\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total: {total}, Success: {successful}, Failed: {failed}\n\n")
        
        for category, category_results in results.items():
            f.write(f"\n{category}\n")
            f.write("-" * len(category) + "\n")
            for result in category_results:
                status = "✓" if result['success'] else "✗"
                f.write(f"{status} {result['prompt']} (view: {result['view']})\n")
                if result['success'] and 'path' in result:
                    f.write(f"  → {result['path']}\n")
    
    print(f"\nResults saved to: {summary_path}")
    
    return successful, failed

def main():
    """Run the test diagram generation."""
    if not os.environ.get('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not set!")
        print("Usage: python generate_all_test_diagrams.py [API_KEY]")
        sys.exit(1)
    
    # Run async generation
    successful, failed = asyncio.run(generate_all_diagrams())
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()