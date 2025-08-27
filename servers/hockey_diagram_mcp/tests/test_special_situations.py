#!/usr/bin/env python3
"""
Test special situations hockey diagrams - power play, penalty kill, 6v5, 3v3 overtime.
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

if len(sys.argv) > 1:
    os.environ['OPENAI_API_KEY'] = sys.argv[1]

from servers.hockey_diagram_mcp.server import generate_hockey_diagram
from servers.hockey_diagram_mcp.two_stage_parser import TwoStageHockeyParser

async def test_single(test_num: int, prompt: str, view: str = "full"):
    """Test a single prompt with detailed output."""
    
    print(f"\n{'='*80}")
    print(f"TEST {test_num}: SPECIAL SITUATIONS TESTING")
    print(f"PROMPT: {prompt}")
    print(f"VIEW: {view}")
    print("="*80)
    
    # Initialize parser
    parser = TwoStageHockeyParser()
    
    # Stage 1: Parse prompt
    print("\n📝 STAGE 1: Two-Stage Parser Analysis")
    print("-" * 50)
    
    try:
        context = {"diagram_type": "tactical", "requested_view": view}
        diagram_spec = await parser.parse_prompt(prompt, context)
        
        print(f"Diagram Type: {diagram_spec.diagram_type}")
        print(f"Title: {diagram_spec.title}")
        print(f"View: {diagram_spec.view}")
        print(f"\nPlayers ({len(diagram_spec.players)}):")
        
        # Analyze player count for special situations
        team_counts = {}
        for i, player in enumerate(diagram_spec.players, 1):
            team = player.team
            if team not in team_counts:
                team_counts[team] = 0
            team_counts[team] += 1
            
            puck_indicator = " 🏒" if player.has_puck else ""
            print(f"  {i}. {player.position} at ({player.x:.1f}, {player.y:.1f}) - Team: {player.team}{puck_indicator}")
                
        # Special situation analysis
        print(f"\nTEAM COMPOSITION:")
        for team, count in team_counts.items():
            print(f"  {team}: {count} players")
            
        # Identify situation type
        if 'attacking' in team_counts and 'defending' in team_counts:
            attacking_count = team_counts['attacking']
            defending_count = team_counts['defending']
            
            if attacking_count == 5 and defending_count == 4:
                print("  🚨 POWER PLAY SITUATION (5v4)")
            elif attacking_count == 4 and defending_count == 5:
                print("  🚨 PENALTY KILL SITUATION (4v5)")
            elif attacking_count == 6 and defending_count == 5:
                print("  🚨 EMPTY NET SITUATION (6v5)")
            elif attacking_count == 3 and defending_count == 3:
                print("  🚨 3v3 OVERTIME SITUATION")
            elif attacking_count == 5 and defending_count == 3:
                print("  🚨 5v3 POWER PLAY")
            elif attacking_count == 3 and defending_count == 5:
                print("  🚨 3v5 PENALTY KILL")
            else:
                print(f"  🚨 UNUSUAL SITUATION ({attacking_count}v{defending_count})")
                
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
        return None, None
    
    # Stage 2: Generate diagram
    print("\n🎨 STAGE 2: Diagram Generation")
    print("-" * 50)
    
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
            
            return diagram_spec, result
            
        else:
            print(f"❌ Generation failed: {result.get('error')}")
            return diagram_spec, None
            
    except Exception as e:
        print(f"❌ Generation Error: {e}")
        return diagram_spec, None

def analyze_special_situation(test_num: int, prompt: str, expected_attacking: int, expected_defending: int, diagram_spec, result):
    """Analyze the results for special situation accuracy."""
    
    print(f"\n🔍 SPECIAL SITUATION ANALYSIS - TEST {test_num}")
    print("-" * 60)
    
    if not diagram_spec:
        print("❌ Cannot analyze - no diagram spec")
        return "Poor"
        
    # Count players by team
    team_counts = {}
    for player in diagram_spec.players:
        team = player.team
        if team not in team_counts:
            team_counts[team] = 0
        team_counts[team] += 1
    
    attacking_count = team_counts.get('attacking', 0)
    defending_count = team_counts.get('defending', 0)
    
    issues = []
    
    # Check player counts
    if attacking_count != expected_attacking:
        issues.append(f"Wrong attacking player count: expected {expected_attacking}, got {attacking_count}")
    
    if defending_count != expected_defending:
        issues.append(f"Wrong defending player count: expected {expected_defending}, got {defending_count}")
    
    # Check positioning for formations
    if "power play" in prompt.lower():
        # Check for typical power play positions
        offensive_zone_players = [p for p in diagram_spec.players if p.x > 25]
        if len(offensive_zone_players) < 4:
            issues.append("Power play should have most players in offensive zone")
            
        # Check for umbrella formation if mentioned
        if "umbrella" in prompt.lower():
            point_players = [p for p in diagram_spec.players if p.y > 40 and p.x > 25]
            if len(point_players) < 1:
                issues.append("Umbrella formation missing point player")
    
    elif "penalty kill" in prompt.lower():
        # Check for compact defensive formation
        defensive_players = [p for p in diagram_spec.players if p.team == 'defending']
        if defensive_players:
            avg_x = sum(p.x for p in defensive_players) / len(defensive_players)
            if avg_x > 0:  # Should be in defensive end
                issues.append("Penalty kill players should be in defensive zone")
    
    elif "6v5" in prompt.lower() or "empty net" in prompt.lower():
        # Check for 6 attacking players
        if attacking_count != 6:
            issues.append("Empty net situation should have 6 attacking players")
        # Check no defending goalie
        defending_goalies = [p for p in diagram_spec.players if p.position == 'G' and p.team == 'defending']
        if defending_goalies:
            issues.append("Empty net situation should not have defending goalie")
    
    elif "3v3" in prompt.lower():
        total_players = attacking_count + defending_count
        if total_players != 6:
            issues.append("3v3 should have exactly 6 skaters total")
        # Check for spread formation
        if diagram_spec.players:
            x_positions = [p.x for p in diagram_spec.players]
            x_range = max(x_positions) - min(x_positions)
            if x_range < 50:  # Should use full ice
                issues.append("3v3 formation should utilize more ice space")
    
    # Strategic positioning check
    strategic_issues = []
    
    if "formation" in prompt.lower():
        # Check if players are positioned in recognizable formation
        if attacking_count >= 5:
            # Check for proper spacing
            attacking_players = [p for p in diagram_spec.players if p.team == 'attacking']
            if len(attacking_players) >= 3:
                y_positions = [p.y for p in attacking_players]
                y_range = max(y_positions) - min(y_positions)
                if y_range < 20:
                    strategic_issues.append("Formation lacks proper width/spacing")
    
    # Generate score
    if not issues and not strategic_issues:
        score = "Good"
        overall_assessment = "Excellent special situation accuracy"
    elif len(issues) <= 1 and len(strategic_issues) <= 1:
        score = "Fair"
        overall_assessment = "Good with minor issues"
    else:
        score = "Poor"
        overall_assessment = "Multiple accuracy problems"
    
    # Output analysis
    print(f"Expected: {expected_attacking}v{expected_defending}")
    print(f"Actual: {attacking_count}v{defending_count}")
    
    if issues:
        print("\n❌ ISSUES IDENTIFIED:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("\n✅ Player counts correct")
    
    if strategic_issues:
        print("\n⚠️ STRATEGIC CONCERNS:")
        for concern in strategic_issues:
            print(f"  • {concern}")
    else:
        print("\n✅ Strategic positioning appropriate")
    
    print(f"\n📊 SCORE: {score}")
    print(f"📋 ASSESSMENT: {overall_assessment}")
    
    return score

# Special situation test cases
SPECIAL_SITUATION_TESTS = [
    # Power Play Tests (5v4)
    (401, "1-3-1 power play umbrella formation with center in bumper position", "offensive", 5, 4),
    (402, "Power play overload formation with 4 players on strong side", "offensive", 5, 4),
    (403, "Box+1 power play with net front presence and perimeter movement", "offensive", 5, 4),
    (404, "Power play diamond formation with quick puck movement", "offensive", 5, 4),
    
    # Penalty Kill Tests (4v5)
    (405, "Box penalty kill formation protecting slot area", "defensive", 4, 5),
    (406, "Diamond penalty kill with aggressive forward pressure", "defensive", 4, 5),
    (407, "Wedge penalty kill formation with triangle in slot", "defensive", 4, 5),
    (408, "Penalty kill with strong side pressure and lane coverage", "defensive", 4, 5),
    
    # 5v3 Power Play Tests
    (409, "5-on-3 power play with box plus one formation", "offensive", 5, 3),
    (410, "5v3 power play spread formation utilizing full width", "offensive", 5, 3),
    
    # 3v5 Penalty Kill Tests  
    (411, "3-on-5 penalty kill with triangle formation", "defensive", 3, 5),
    (412, "5v3 penalty kill protecting middle and blocking shots", "defensive", 3, 5),
    
    # Empty Net Situations (6v5)
    (413, "6v5 empty net attack with extra attacker high", "offensive", 6, 5),
    (414, "Empty net situation with goalie pulled and 6 forwards", "offensive", 6, 5),
    (415, "6 on 5 power play with empty net late game", "offensive", 6, 5),
    
    # 3v3 Overtime Tests
    (416, "3v3 overtime formation with spread positioning", "full", 3, 3),
    (417, "3 on 3 overtime with triangle formation and speed", "full", 3, 3),
    (418, "3v3 overtime breakout with stretch pass opportunity", "full", 3, 3),
    (419, "Three on three overtime cycle with quick transitions", "full", 3, 3),
]

async def main():
    """Run special situation tests."""
    
    if not os.environ.get('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not set!")
        print("Usage: python test_special_situations.py [API_KEY] [test_number]")
        sys.exit(1)
        
    # Get test number
    test_num = int(sys.argv[2]) if len(sys.argv) > 2 else 401
    
    # Find test case
    test_case = None
    for case in SPECIAL_SITUATION_TESTS:
        if case[0] == test_num:
            test_case = case
            break
    
    if not test_case:
        print(f"Error: Test number {test_num} not found in special situations")
        print("Available tests: 401-419")
        sys.exit(1)
        
    test_id, prompt, view, expected_attacking, expected_defending = test_case
    
    print(f"Running Special Situation Test {test_id}")
    print(f"Expected: {expected_attacking}v{expected_defending}")
    
    # Run test
    diagram_spec, result = await test_single(test_id, prompt, view)
    
    # Analyze results
    score = analyze_special_situation(test_id, prompt, expected_attacking, expected_defending, diagram_spec, result)
    
    # Generate markdown report
    print(f"\n{'='*80}")
    print("MARKDOWN REPORT")
    print("="*80)
    
    situation_type = ""
    if expected_attacking == 5 and expected_defending == 4:
        situation_type = "Power Play (5v4)"
    elif expected_attacking == 4 and expected_defending == 5:
        situation_type = "Penalty Kill (4v5)" 
    elif expected_attacking == 6 and expected_defending == 5:
        situation_type = "Empty Net (6v5)"
    elif expected_attacking == 3 and expected_defending == 3:
        situation_type = "3v3 Overtime"
    elif expected_attacking == 5 and expected_defending == 3:
        situation_type = "5v3 Power Play"
    elif expected_attacking == 3 and expected_defending == 5:
        situation_type = "3v5 Penalty Kill"
    
    print(f"""
## Test {test_id}: {situation_type}
- **Prompt Used**: "{prompt}"
- **Expected**: {expected_attacking}v{expected_defending} formation with proper positioning
- **Actual**: {len(diagram_spec.players) if diagram_spec else 'N/A'} total players ({diagram_spec and sum(1 for p in diagram_spec.players if p.team == 'attacking') or 'N/A'} attacking, {diagram_spec and sum(1 for p in diagram_spec.players if p.team == 'defending') or 'N/A'} defending)
- **Issues**: {"None identified" if score == "Good" else "Player count or positioning concerns"}
- **Score**: {score}
- **Suggestions**: {"Excellent execution" if score == "Good" else "Review special teams positioning and player count accuracy"}
""")
    
    # Show next test
    next_test = test_id + 1
    if next_test <= 419:
        print(f"\nNext test: python test_special_situations.py [API_KEY] {next_test}")
    else:
        print(f"\nAll special situation tests complete!")

if __name__ == "__main__":
    asyncio.run(main())