#!/usr/bin/env python3
"""Test all movement patterns visually"""

import sys
sys.path.append('.')

from src.hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation

# Create drill spec to showcase movement patterns
spec = DiagramSpec(
    title="Movement Pattern Showcase",
    rink={
        "view": "full",
        "zone": "full",
        "xlim": [-100, 100],
        "ylim": [-42.5, 42.5]
    },
    players=[
        # Offensive zone patterns
        Player(type="forward", position="P1", coordinates={"x": 89, "y": 36}, label="Rim"),
        Player(type="forward", position="P2", coordinates={"x": 0, "y": 0}, label="Dump"),
        Player(type="forward", position="P3", coordinates={"x": 30, "y": 20}, label="Sauce"),
        Player(type="forward", position="P4", coordinates={"x": 89, "y": 0}, label="Wrap"),
        
        # Neutral zone patterns
        Player(type="forward", position="P5", coordinates={"x": -10, "y": 15}, label="Button"),
        Player(type="forward", position="P6", coordinates={"x": -50, "y": -20}, label="Stretch"),
        
        # Defensive zone patterns
        Player(type="defense", position="P7", coordinates={"x": -69, "y": 22.5}, label="Bank"),
        Player(type="forward", position="P8", coordinates={"x": -89, "y": -36}, label="Chip"),
        
        # Cross-ice and drive patterns
        Player(type="forward", position="P9", coordinates={"x": 69, "y": 38}, label="Cross"),
        Player(type="forward", position="P10", coordinates={"x": 85, "y": -36}, label="Drive"),
    ],
    movements=[
        # Rim pattern - along boards behind net
        Movement(
            type="pass",
            from_pos={"x": 89, "y": 36},
            to_pos={"x": 89, "y": -36},
            style="dotted",
            waypoints=[
                [89, 38],  # To boards
                [89, 38],  # Along boards to corner
                [89, 0],   # Behind net
                [89, -38], # To other corner
                [89, -36]  # Final position
            ],
            label="Rim"
        ),
        
        # Dump pattern - high and deep
        Movement(
            type="pass",
            from_pos={"x": 0, "y": 0},
            to_pos={"x": 89, "y": 36},
            style="dotted",
            waypoints=[
                [26.7, 7.2],  # Initial trajectory
                [85, 35]      # High into corner
            ],
            label="Dump"
        ),
        
        # Sauce pattern - elevated pass
        Movement(
            type="pass",
            from_pos={"x": 30, "y": 20},
            to_pos={"x": 69, "y": 0},
            style="dotted",
            waypoints=[
                [49.5, 18]  # Arc over obstacles
            ],
            label="Sauce"
        ),
        
        # Wrap pattern - around net
        Movement(
            type="carry",
            from_pos={"x": 89, "y": 0},
            to_pos={"x": 83, "y": -15},
            style="wavy",
            waypoints=[
                [89, 7.5],   # Start wrap
                [85, -15]    # Come around
            ],
            label="Wrap"
        ),
        
        # Button hook pattern - curl back
        Movement(
            type="skate",
            from_pos={"x": -10, "y": 15},
            to_pos={"x": 25, "y": 10},
            style="solid",
            waypoints=[
                [1.75, 15],    # Forward
                [-10.25, 7],   # Start curl
                [-22, 15],     # Complete curl
                [25, 10]       # Continue
            ],
            label="Button Hook"
        ),
        
        # Stretch pass - long outlet
        Movement(
            type="pass",
            from_pos={"x": -50, "y": -20},
            to_pos={"x": 50, "y": 20},
            style="dotted",
            waypoints=[
                [0, 3]  # Slight arc for realism
            ],
            label="Stretch"
        ),
        
        # Bank pass - off boards
        Movement(
            type="pass",
            from_pos={"x": -69, "y": 22.5},
            to_pos={"x": -50, "y": 0},
            style="dotted",
            waypoints=[
                [-59.5, 40]  # Hit boards
            ],
            label="Bank"
        ),
        
        # Chip pattern - quick advance
        Movement(
            type="carry",
            from_pos={"x": -89, "y": -36},
            to_pos={"x": -60, "y": -20},
            style="wavy",
            waypoints=[
                [-77.4, -29.6]  # Small arc
            ],
            label="Chip"
        ),
        
        # Cross-ice pattern - S-curve
        Movement(
            type="skate",
            from_pos={"x": 69, "y": 38},
            to_pos={"x": 69, "y": -38},
            style="solid",
            waypoints=[
                [69, 22.8],   # S-curve point 1
                [69, -22.8]   # S-curve point 2
            ],
            label="Cross-ice"
        ),
        
        # Drive pattern - to net
        Movement(
            type="carry",
            from_pos={"x": 85, "y": -36},
            to_pos={"x": 83, "y": 0},
            style="wavy",
            waypoints=[
                [85.6, -28.8],  # Start drive
                [75, -5]        # Curve to net
            ],
            label="Drive"
        )
    ],
    zones=[],
    annotations=[
        Annotation(
            text="Hockey Movement Patterns Test",
            position={"x": 0, "y": -48},
            size="large",
            style="bold"
        ),
        Annotation(
            text="All 10 patterns: Rim, Dump, Sauce, Wrap, Button Hook, Stretch, Bank, Chip, Cross-ice, Drive",
            position={"x": 0, "y": -52},
            size="small"
        )
    ],
    metadata={}
)

# Build the diagram
builder = DiagramBuilder()
output_file = "test_movement_patterns"
fig = builder.build(spec, output_file)
print(f"✅ Generated: {output_file}.png")