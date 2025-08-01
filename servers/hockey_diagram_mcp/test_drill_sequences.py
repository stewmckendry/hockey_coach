#!/usr/bin/env python3
"""
Test Case 4: Drill Sequences - Step-by-step visualization of hockey drills
Tests the system's ability to show progressive movements with numbered sequences.
"""

import asyncio
import json
from pathlib import Path
from generator import HockeyDiagramGenerator
from enhanced_parser import EnhancedHockeyParser, DiagramSpec, PlayerPosition, MovementSpec

async def generate_drill_tests():
    """Generate drill sequence test cases."""
    generator = HockeyDiagramGenerator()
    # Parser not needed for hard-coded tests
    # parser = EnhancedHockeyParser()
    
    # Test 4.1: Basic Passing Drill (Triangle)
    drill_1 = DiagramSpec(
        players=[
            PlayerPosition(position="C", x=-20, y=0, team="home", has_puck=True, step=1),
            PlayerPosition(position="LW", x=0, y=20, team="home", has_puck=False, step=2),
            PlayerPosition(position="RW", x=0, y=-20, team="home", has_puck=False, step=3),
        ],
        movements=[
            MovementSpec(
                from_position="C", 
                to_position="LW", 
                movement_type="pass", 
                sequence=1,
                arrow_style="solid"
            ),
            MovementSpec(
                from_position="LW", 
                to_position="RW", 
                movement_type="pass", 
                sequence=2,
                arrow_style="solid"
            ),
            MovementSpec(
                from_position="RW", 
                to_position="C", 
                movement_type="pass", 
                sequence=3,
                arrow_style="solid"
            ),
        ],
        view="neutral",
        title="Triangle Passing Drill",
        diagram_type="drill"
    )
    
    spec_1 = drill_1.model_dump()
    image_1 = generator.generate_diagram(spec_1)
    filepath_1 = Path("test_drill_1_triangle_passing.png")
    generator.save_image(image_1, filepath_1)
    print(f"Generated: {filepath_1}")
    
    # Test 4.2: Breakout Drill (D to D pass)
    drill_2 = DiagramSpec(
        players=[
            # Initial positions
            PlayerPosition(position="LD", x=-70, y=20, team="home", has_puck=True, step=1),
            PlayerPosition(position="RD", x=-70, y=-20, team="home", has_puck=False),
            PlayerPosition(position="C", x=-30, y=0, team="home", has_puck=False),
            PlayerPosition(position="LW", x=-40, y=35, team="home", has_puck=False),
            PlayerPosition(position="RW", x=-40, y=-35, team="home", has_puck=False),
            PlayerPosition(position="G", x=-89, y=0, team="home", has_puck=False),
        ],
        movements=[
            # Step 1: D to D pass
            MovementSpec(
                from_position="LD", 
                to_position="RD", 
                movement_type="pass", 
                sequence=1,
                arrow_style="solid"
            ),
            # Step 2: RD to RW on boards
            MovementSpec(
                from_position="RD", 
                to_position="RW", 
                movement_type="pass", 
                sequence=2,
                arrow_style="solid"
            ),
            # Step 3: RW skates up ice
            MovementSpec(
                from_position="RW", 
                to_position=[0, -35], 
                movement_type="skating", 
                sequence=3,
                arrow_style="dashed"
            ),
            # Step 4: Center support
            MovementSpec(
                from_position="C", 
                to_position=[0, 0], 
                movement_type="skating", 
                sequence=3,
                arrow_style="dashed"
            ),
        ],
        view="full",
        title="Breakout Drill - D to D Pass",
        diagram_type="drill"
    )
    
    spec_2 = drill_2.model_dump()
    image_2 = generator.generate_diagram(spec_2)
    filepath_2 = Path("test_drill_2_breakout.png")
    generator.save_image(image_2, filepath_2)
    print(f"Generated: {filepath_2}")
    
    # Test 4.3: 2v1 Rush Drill
    drill_3 = DiagramSpec(
        players=[
            # Offensive players
            PlayerPosition(position="LW", x=20, y=25, team="home", has_puck=True, step=1),
            PlayerPosition(position="C", x=20, y=-10, team="home", has_puck=False),
            # Defender
            PlayerPosition(position="X1", x=40, y=0, team="away", has_puck=False),
            # Supporting players
            PlayerPosition(position="RW", x=-20, y=-35, team="home", has_puck=False),
            PlayerPosition(position="XG", x=89, y=0, team="away", has_puck=False),
        ],
        movements=[
            # Step 1: LW carries puck forward
            MovementSpec(
                from_position="LW", 
                to_position=[50, 20], 
                movement_type="skating", 
                sequence=1,
                arrow_style="solid"
            ),
            # Step 2: Pass to C
            MovementSpec(
                from_position="LW", 
                to_position="C", 
                movement_type="pass", 
                sequence=2,
                arrow_style="solid"
            ),
            # Step 3: C drives to net
            MovementSpec(
                from_position="C", 
                to_position=[75, -5], 
                movement_type="skating", 
                sequence=3,
                arrow_style="solid"
            ),
            # Step 4: Shot on goal
            MovementSpec(
                from_position="C", 
                to_position="XG", 
                movement_type="shot", 
                sequence=4,
                arrow_style="solid"
            ),
            # Defender backskates
            MovementSpec(
                from_position="X1", 
                to_position=[60, 0], 
                movement_type="skating", 
                sequence=1,
                arrow_style="dotted"
            ),
        ],
        zones=[
            # Highlight attack lane
            {"zone_type": "pressure", "area": [40, -20, 40, 40], "team": "home", "opacity": 0.2}
        ],
        view="offensive",
        title="2v1 Rush Drill",
        diagram_type="drill"
    )
    
    spec_3 = drill_3.model_dump()
    image_3 = generator.generate_diagram(spec_3)
    filepath_3 = Path("test_drill_3_2v1_rush.png")
    generator.save_image(image_3, filepath_3)
    print(f"Generated: {filepath_3}")
    
    return [filepath_1, filepath_2, filepath_3]

if __name__ == "__main__":
    print("Generating Test Case 4: Drill Sequences...")
    print("=" * 60)
    
    filepaths = asyncio.run(generate_drill_tests())
    
    print("\nTest Case 4 Complete!")
    print("Generated drill sequence diagrams:")
    for fp in filepaths:
        print(f"  - {fp}")
    print("\nDrill tests demonstrate:")
    print("  1. Step-by-step progression visualization")
    print("  2. Multiple movement types (pass, skate, shot)")
    print("  3. Sequence numbering for drill flow")
    print("  4. Different arrow styles for movement types")