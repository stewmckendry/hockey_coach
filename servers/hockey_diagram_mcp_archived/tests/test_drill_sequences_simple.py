#!/usr/bin/env python3
"""
Test Case 4: Drill Sequences - Simplified version using correct data structures
"""

from pathlib import Path
from generator import HockeyDiagramGenerator, Player, Movement, Zone

def generate_drill_tests():
    """Generate drill sequence test cases."""
    generator = HockeyDiagramGenerator()
    
    # Test 4.1: Basic Passing Drill (Triangle)
    players_1 = [
        Player(position="C", x=-20, y=0, team="home", has_puck=True),
        Player(position="LW", x=0, y=20, team="home", has_puck=False),
        Player(position="RW", x=0, y=-20, team="home", has_puck=False),
    ]
    
    movements_1 = [
        Movement(
            from_position="C", 
            to_position="LW", 
            movement_type="pass"
        ),
        Movement(
            from_position="LW", 
            to_position="RW", 
            movement_type="pass"
        ),
        Movement(
            from_position="RW", 
            to_position="C", 
            movement_type="pass"
        ),
    ]
    
    image_1 = generator.generate_diagram(
        players=players_1,
        movements=movements_1,
        view="neutral",
        title="Triangle Passing Drill"
    )
    filepath_1 = Path("test_drill_1_triangle_passing.png")
    generator.save_to_file(image_1, str(filepath_1))
    print(f"Generated: {filepath_1}")
    
    # Test 4.2: Breakout Drill (D to D pass)
    players_2 = [
        # Initial positions
        Player(position="LD", x=-70, y=20, team="home", has_puck=True),
        Player(position="RD", x=-70, y=-20, team="home", has_puck=False),
        Player(position="C", x=-30, y=0, team="home", has_puck=False),
        Player(position="LW", x=-40, y=35, team="home", has_puck=False),
        Player(position="RW", x=-40, y=-35, team="home", has_puck=False),
        Player(position="G", x=-89, y=0, team="home", has_puck=False),
    ]
    
    movements_2 = [
        # Step 1: D to D pass
        Movement(
            from_position="LD", 
            to_position="RD", 
            movement_type="pass"
        ),
        # Step 2: RD to RW on boards
        Movement(
            from_position="RD", 
            to_position="RW", 
            movement_type="pass"
        ),
    ]
    
    image_2 = generator.generate_diagram(
        players=players_2,
        movements=movements_2,
        view="full",
        title="Breakout Drill - D to D Pass"
    )
    filepath_2 = Path("test_drill_2_breakout.png")
    generator.save_to_file(image_2, str(filepath_2))
    print(f"Generated: {filepath_2}")
    
    # Test 4.3: 2v1 Rush Drill
    players_3 = [
        # Offensive players
        Player(position="LW", x=20, y=25, team="home", has_puck=True),
        Player(position="C", x=20, y=-10, team="home", has_puck=False),
        # Defender
        Player(position="X1", x=40, y=0, team="away", has_puck=False),
        # Goalie
        Player(position="XG", x=89, y=0, team="away", has_puck=False),
    ]
    
    movements_3 = [
        # Pass to C
        Movement(
            from_position="LW", 
            to_position="C", 
            movement_type="pass"
        ),
        # Shot on goal
        Movement(
            from_position="C", 
            to_position=(85, 0), 
            movement_type="shot"
        ),
    ]
    
    zones_3 = [
        # Highlight attack lane
        Zone(zone_type="pressure", area=(40, -20, 40, 40), team="home")
    ]
    
    image_3 = generator.generate_diagram(
        players=players_3,
        movements=movements_3,
        zones=zones_3,
        view="offensive",
        title="2v1 Rush Drill"
    )
    filepath_3 = Path("test_drill_3_2v1_rush.png")
    generator.save_to_file(image_3, str(filepath_3))
    print(f"Generated: {filepath_3}")
    
    return [filepath_1, filepath_2, filepath_3]

if __name__ == "__main__":
    print("Generating Test Case 4: Drill Sequences...")
    print("=" * 60)
    
    filepaths = generate_drill_tests()
    
    print("\nTest Case 4 Complete!")
    print("Generated drill sequence diagrams:")
    for fp in filepaths:
        print(f"  - {fp}")
    print("\nDrill tests demonstrate:")
    print("  1. Step-by-step progression visualization")
    print("  2. Multiple movement types (pass, skate, shot)")
    print("  3. Different drill complexities")
    print("  4. Zone highlighting for tactical emphasis")