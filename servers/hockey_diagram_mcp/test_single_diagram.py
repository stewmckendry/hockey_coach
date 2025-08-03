#!/usr/bin/env python3
"""
Test a single diagram with detailed output for review.
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
sys.path.append(str(Path(__file__).resolve().parent))

if len(sys.argv) > 1:
    os.environ['OPENAI_API_KEY'] = sys.argv[1]

from server import generate_hockey_diagram
from two_stage_parser import TwoStageHockeyParser

async def test_single(prompt: str, view: str = "full"):
    """Test a single prompt with detailed output."""
    
    print(f"\n{'='*60}")
    print(f"PROMPT: {prompt}")
    print(f"VIEW: {view}")
    print("="*60)
    
    # Initialize parser
    parser = TwoStageHockeyParser()
    
    # Stage 1: Parse prompt
    print("\n📝 STAGE 1: Two-Stage Parser")
    print("-" * 40)
    
    try:
        context = {"diagram_type": "tactical", "requested_view": view}
        diagram_spec = await parser.parse_prompt(prompt, context)
        
        print(f"Diagram Type: {diagram_spec.diagram_type}")
        print(f"Title: {diagram_spec.title}")
        print(f"View: {diagram_spec.view}")
        print(f"\nPlayers ({len(diagram_spec.players)}):")
        for i, player in enumerate(diagram_spec.players, 1):
            print(f"  {i}. {player.position} at ({player.x:.1f}, {player.y:.1f}) - Team: {player.team}")
            if player.has_puck:
                print(f"     → Has puck!")
                
        if diagram_spec.movements:
            print(f"\nMovements ({len(diagram_spec.movements)}):")
            for i, movement in enumerate(diagram_spec.movements, 1):
                to_pos = movement.to_position
                if isinstance(to_pos, list):
                    to_pos = f"({to_pos[0]:.1f}, {to_pos[1]:.1f})"
                print(f"  {i}. {movement.from_position} → {to_pos} ({movement.movement_type})")
                
        if diagram_spec.zones:
            print(f"\nZones ({len(diagram_spec.zones)}):")
            for i, zone in enumerate(diagram_spec.zones, 1):
                print(f"  {i}. {zone.zone_type} - {zone.area} (Team: {zone.team})")
                
    except Exception as e:
        print(f"❌ Parser Error: {e}")
        return
    
    # Stage 2: Generate diagram
    print("\n🎨 STAGE 2: Diagram Generation")
    print("-" * 40)
    
    try:
        result = await generate_hockey_diagram(
            prompt=prompt,
            view=view,
            output_format="png"
        )
        
        if result['success']:
            print(f"✅ Success!")
            print(f"Diagram saved to: {result['diagram_path']}")
            print(f"Generation time: {result['generation_time']:.2f}s")
            
            # QA Analysis
            print("\n🔍 QA ANALYSIS")
            print("-" * 40)
            
            # Check player positioning
            spec = result['diagram_spec']
            players = spec['players']
            
            # View consistency check
            if view != spec['view']:
                print(f"⚠️  View mismatch: requested '{view}', got '{spec['view']}'")
            else:
                print(f"✅ View correct: {view}")
                
            # Zone positioning check
            out_of_zone = []
            for player in players:
                x = player['x']
                if view == "offensive" and x < 25:
                    out_of_zone.append(f"{player['position']} at x={x}")
                elif view == "defensive" and x > -25:
                    out_of_zone.append(f"{player['position']} at x={x}")
                elif view == "neutral" and (x < -25 or x > 25):
                    out_of_zone.append(f"{player['position']} at x={x}")
                    
            if out_of_zone:
                print(f"⚠️  Players out of zone: {', '.join(out_of_zone)}")
            else:
                print(f"✅ All players in correct zone")
                
            # Movement check
            expected_movements = any(word in prompt.lower() for word in ['pass', 'movement', 'rush', 'breakout', 'cycle'])
            has_movements = len(spec.get('movements', [])) > 0
            
            if expected_movements and not has_movements:
                print(f"⚠️  Expected movements but none found")
            elif has_movements:
                print(f"✅ Movements included: {len(spec['movements'])}")
            else:
                print(f"✅ No movements expected or found")
                
        else:
            print(f"❌ Generation failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Generation Error: {e}")

# Test cases
TEST_CASES = [
    # Batch 1: Views
    ("5v5 neutral zone setup", "full"),
    ("Offensive zone cycle play", "offensive"),
    ("Defensive zone coverage", "defensive"),
    ("Neutral zone trap 1-3-1", "neutral"),
    ("Breakout from defensive zone to offensive rush", "full"),
    
    # Batch 2: Formations
    ("2-1-2 forecheck with F1 behind net", "offensive"),
    ("Box penalty kill formation", "defensive"),
    ("1-3-1 power play umbrella", "offensive"),
    ("Diamond penalty kill aggressive pressure", "defensive"),
    ("2-3 forecheck neutral zone pressure", "neutral"),
    
    # Batch 3: Drills
    ("3v2 rush drill from center ice", "full"),
    ("Triangle passing drill in neutral zone", "neutral"),
    ("2v1 defensive drill starting at blue line", "defensive"),
    ("Breakout drill with D-to-D pass behind net", "defensive"),
    ("Power play entry drill at offensive blue line", "offensive"),
    
    # Batch 4: Plays
    ("D-to-D breakout with center swinging low", "defensive"),
    ("Give and go play through neutral zone", "full"),
    ("Cycle play with low-to-high pass for shot", "offensive"),
    ("Stretch pass from D to winger for breakaway", "full"),
    ("Behind the net play with wrap around attempt", "offensive"),
    
    # Batch 5: Special
    ("6v5 with goalie pulled offensive zone setup", "offensive"),
    ("3v3 overtime spread formation", "full"),
    ("Faceoff play in defensive zone strong side win", "defensive"),
    ("Power play with net front screen and point shot", "offensive"),
    ("Penalty kill clear with strong side winger support", "defensive"),
    
    # Batch 6: Formation Tests (Tests 101+)
    ("2-1-2 forecheck with F1 pressuring puck carrier behind net and F2 supporting", "offensive"),
    ("1-3-1 neutral zone trap with F1 pressuring and three players forming barrier", "neutral"),
    ("Box penalty kill formation with four players in square defensive setup", "defensive"),
    ("Diamond penalty kill formation with tight slot protection", "defensive"),
    ("2-1-2 forecheck aggressive pressure with wingers high in offensive zone", "offensive"),
    ("1-3-1 neutral zone trap forcing dump-ins with disciplined positioning", "neutral"),
    ("Box penalty kill maintaining square formation against power play", "defensive"),
    ("Diamond penalty kill with point man high and low support", "defensive")
]

async def main():
    """Run single test."""
    
    if not os.environ.get('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not set!")
        print("Usage: python test_single_diagram.py [API_KEY] [test_number_or_prompt] [view]")
        print("Examples:")
        print("  python test_single_diagram.py $API_KEY 0  # Run preset test 0")
        print("  python test_single_diagram.py $API_KEY \"2-1-2 forecheck\" offensive")
        sys.exit(1)
    
    # Check if second argument is a number (preset test) or string (custom prompt)
    if len(sys.argv) > 2:
        try:
            # Try to parse as test number
            test_num = int(sys.argv[2])
            
            if test_num >= len(TEST_CASES):
                print(f"Error: Test number {test_num} out of range (0-{len(TEST_CASES)-1})")
                sys.exit(1)
                
            prompt, view = TEST_CASES[test_num]
            
            # Display test number starting from 101 for formation tests (index 25+)
            display_test_num = test_num + 101 if test_num >= 25 else test_num + 1
            
            print(f"Running preset test {display_test_num}/{len(TEST_CASES)}")
            await test_single(prompt, view)
            
            next_display_num = test_num + 102 if test_num >= 24 else test_num + 2
            print(f"\nNext test: python test_single_diagram.py [API_KEY] {test_num + 1} (Test {next_display_num})")
            
        except ValueError:
            # Not a number, treat as custom prompt
            prompt = sys.argv[2]
            view = sys.argv[3] if len(sys.argv) > 3 else "full"
            
            print(f"Running custom test with prompt: \"{prompt}\"")
            await test_single(prompt, view)
    else:
        # No arguments, run test 0
        prompt, view = TEST_CASES[0]
        print(f"Running preset test 1/{len(TEST_CASES)}")
        await test_single(prompt, view)
        print(f"\nNext test: python test_single_diagram.py [API_KEY] 1 (Test 2)")

if __name__ == "__main__":
    asyncio.run(main())