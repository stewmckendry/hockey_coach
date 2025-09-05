#!/usr/bin/env python3
"""
Drill 4: 3v3 Battle
Small area competitive game with two nets and mandatory coach pass.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hockey_diagram_builder import (
    DiagramBuilder, DiagramSpec, 
    Player, Movement, Zone, Annotation
)
from drill_utilities import (
    Z_ORDER, STANDARD_POSITIONS, ANGLES,
    create_standard_annotations
)

def create_drill_4():
    """Create Drill 4: 3v3 Battle diagram."""
    
    # Players - 3v3 setup with strategic positioning
    players = []
    
    # Player queues in neutral zone
    # Home team queue (left side of coach)
    for i in range(3):
        players.append(Player(
            type='forward',
            position=f'Q{i+1}',
            coordinates={'x': 10, 'y': 15 - (i * 4)},  # Neutral zone, left side
            team='home',
            label='X'
        ))
    
    # Away team queue (right side of coach)
    for i in range(3):
        players.append(Player(
            type='forward',
            position=f'Q{i+4}',
            coordinates={'x': 10, 'y': -15 + (i * 4)},  # Neutral zone, right side
            team='away',
            label='O'
        ))
    
    # Home team (blue) - offensive positioning
    players.append(Player(
        type='forward',
        position='X1',
        coordinates={'x': 65, 'y': 15},  # High slot
        team='home',
        has_puck=True,  # Starting with puck
        label='X1'
    ))
    players.append(Player(
        type='forward',
        position='X2',
        coordinates={'x': 75, 'y': -20},  # Low corner
        team='home',
        label='X2'
    ))
    players.append(Player(
        type='forward',
        position='X3',
        coordinates={'x': 55, 'y': 0},  # Mid-slot support
        team='home',
        label='X3'
    ))
    
    # Away team (red) - defensive positioning
    players.append(Player(
        type='forward',
        position='O1',
        coordinates={'x': 60, 'y': 10},  # Covering X1
        team='away',
        label='O1'
    ))
    players.append(Player(
        type='forward',
        position='O2',
        coordinates={'x': 70, 'y': -15},  # Covering X2
        team='away',
        label='O2'
    ))
    players.append(Player(
        type='forward',
        position='O3',
        coordinates={'x': 50, 'y': -5},  # Covering X3
        team='away',
        label='O3'
    ))
    
    # Coaches positioned at boards/hashmarks
    players.append(Player(
        type='coach',
        position='C1',
        coordinates={'x': 30, 'y': 0},  # Inside blue line (offensive zone)
        team='home',
        label='C'
    ))
    players.append(Player(
        type='coach',
        position='C2',
        coordinates={'x': 69, 'y': 40},  # Right boards near hashmark
        team='home',
        label='C'
    ))
    players.append(Player(
        type='coach',
        position='C3',
        coordinates={'x': 69, 'y': -40},  # Left boards near hashmark
        team='home',
        label='C'
    ))
    
    # Goalies in both nets
    players.append(Player(
        type='goalie',
        position='G1',
        coordinates={'x': 83, 'y': 0},  # Regular crease
        team='away',
        label='G'
    ))
    players.append(Player(
        type='goalie',
        position='G2',
        coordinates={'x': 55, 'y': 0},  # Moved closer to main net
        team='home',
        label='G'
    ))
    
    # Add single puck on ice
    players.append(Player(
        type='puck',
        position='puck',
        coordinates={'x': 65, 'y': 15},  # Start with X1
        team='home',
        label=None
    ))
    
    # No movements - just show positioning
    movements = []
    
    # Zones for nets (proper net drawings)
    zones = []
    
    # Second net representation (moved closer to main net)
    # Create a more realistic net shape
    # Net back/frame (dark red)
    zones.append(Zone(
        type='coverage',
        shape='rectangle',
        bounds={'x': 54, 'y': -3, 'width': 3, 'height': 6},
        team='away',
        opacity=0.9,
        color='darkred',
        label=''
    ))
    
    # Net opening (white/light)
    zones.append(Zone(
        type='coverage',
        shape='rectangle',
        bounds={'x': 53, 'y': -2.5, 'width': 1, 'height': 5},
        team='home',
        opacity=0.8,
        color='white',
        label=''
    ))
    
    # Net mesh pattern (gray lines)
    zones.append(Zone(
        type='coverage',
        shape='rectangle',
        bounds={'x': 54.5, 'y': -2.5, 'width': 2, 'height': 5},
        team='away',
        opacity=0.3,
        color='gray',
        label=''
    ))
    
    # No annotations to avoid cutoff
    annotations = []
    
    # Create diagram spec
    spec = DiagramSpec(
        title='Drill 4: 3v3 Battle - Competitive Small Area Game',
        rink={'view': 'custom', 'xlim': (0, 100), 'ylim': (-42.5, 42.5)},  # Offensive + neutral zones
        players=players,
        movements=movements,
        zones=zones,
        annotations=annotations,
        metadata={
            'drill_type': '3v3 Battle',
            'skill_focus': ['compete', 'transitions', 'positioning', 'passing'],
            'duration': '45-60 seconds per shift',
            'age_group': 'U14+'
        }
    )
    
    return spec


def main():
    """Generate and save the drill diagram."""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'outputs'
    )
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create diagram
    spec = create_drill_4()
    builder = DiagramBuilder()
    
    # Save diagram
    output_path = os.path.join(output_dir, f'drill4_3v3_battle_{timestamp}.png')
    result_path = builder.build(spec, output_path)
    print(f"Diagram saved to: {result_path}")
    
    # Also save JSON spec
    json_path = os.path.join(output_dir, f'drill4_3v3_battle_{timestamp}.json')
    with open(json_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    print(f"JSON spec saved to: {json_path}")
    
    return result_path, json_path


if __name__ == '__main__':
    main()