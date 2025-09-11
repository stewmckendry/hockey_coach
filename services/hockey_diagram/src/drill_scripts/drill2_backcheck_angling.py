#!/usr/bin/env python
"""
Drill 2: Backcheck & Angling
Final script from iteration 9
Created: 2025-08-27

This drill practices defensive backchecking and angling techniques.
- Offensive player makes wide loop through neutral zone
- Defensive player crosses ice to far side pylon
- Players intercept at blue line (outside the house)
"""

import sys
import numpy as np
from datetime import datetime
from pathlib import Path
sys.path.append('..')

from hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation
from drill_utilities import generate_arc_points, STANDARD_POSITIONS, Z_ORDER

def create_drill2_diagram(output_path=None):
    """Create Drill 2: Backcheck & Angling diagram"""
    
    spec = DiagramSpec(
        title='Drill 2: Backcheck & Angling',
        rink={'view': 'full', 'show_zones': True, 'show_faceoff_dots': True},
        players=[
            # Line 1 - WITH PUCKS (bottom left corner)
            Player(type='forward', position='O1', coordinates={'x': -75, 'y': -38},
                   team='home', has_puck=False, label='X'),
            Player(type='forward', position='O', coordinates={'x': -80, 'y': -38},
                   team='home', has_puck=False, label='X'),
            Player(type='forward', position='O', coordinates={'x': -85, 'y': -38},
                   team='home', has_puck=False, label='X'),

            # Pucks beside the queue (just black dots)
            Player(type='puck', position='P1', coordinates={'x': -70, 'y': -38},
                   team='neutral', has_puck=False),
            Player(type='puck', position='P2', coordinates={'x': -70, 'y': -36},
                   team='neutral', has_puck=False),
            Player(type='puck', position='P3', coordinates={'x': -70, 'y': -34},
                   team='neutral', has_puck=False),

            # Line 2 - WITHOUT PUCKS (top left corner)
            Player(type='forward', position='D1', coordinates={'x': -75, 'y': 38},
                   team='home', has_puck=False, label='X'),
            Player(type='forward', position='D', coordinates={'x': -80, 'y': 38},
                   team='home', has_puck=False, label='X'),
            Player(type='forward', position='D', coordinates={'x': -85, 'y': 38},
                   team='home', has_puck=False, label='X'),

            # Goalie (on top of crease)
            Player(type='goalie', position='G', coordinates={'x': -83, 'y': 0},
                   team='home', label='G'),
        ],
        movements=[],
        zones=[
            # Use triangle pylons (polygon shape)
            Zone(type='cone', shape='polygon',
                 bounds={'x': -15, 'y': -15, 'vertices': [(-15, -12), (-17, -17), (-13, -17)]},
                 team='neutral', opacity=1.0, color='darkorange', label=''),

            # Pylon at TOP of the LEFT faceoff circle
            Zone(type='cone', shape='polygon',
                 bounds={'x': -50, 'y': -22.5, 'vertices': [(-50, -20), (-52, -25), (-48, -25)]},
                 team='neutral', opacity=1.0, color='darkorange', label=''),

            # Defensive zone highlight (keep low opacity for background)
            Zone(type='coverage', shape='rectangle',
                 bounds={'x': -62.5, 'y': 0, 'width': 37.5, 'height': 85},
                 team='home', opacity=0.02, color='blue', label='')
        ],
        annotations=[
            Annotation(text='Key Points:', position={'x': 0, 'y': 35},
                      size='medium', style='bold'),
            Annotation(text='• Offensive player makes wide loop through neutral zone',
                      position={'x': 0, 'y': 32}, size='small', style='normal'),
            Annotation(text='• Defensive player crosses ice to far side pylon',
                      position={'x': 0, 'y': 30}, size='small', style='normal'),
            Annotation(text='• Intercept at blue line - outside the house',
                      position={'x': 0, 'y': 28}, size='small', style='normal'),

            # Label the lines
            Annotation(text='Pucks', position={'x': -70, 'y': -41},
                      size='small', style='normal')
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'age_group': 'U11',
            'skill_level': 'intermediate',
            'drill_type': 'defensive'
        }
    )

    # Create movements
    movements = []

    # OFFENSIVE PATH
    # 1. Start from corner, head up ice
    movements.append(Movement(type='carry', from_pos={'x': -75, 'y': -38},
                             to_pos={'x': -40, 'y': -35}, style='solid', with_puck=True, label=''))

    # 2. Continue toward neutral zone, starting to curve
    movements.append(Movement(type='carry', from_pos={'x': -40, 'y': -35},
                             to_pos={'x': -20, 'y': -25}, style='solid', with_puck=True, label=''))

    # 3. Wide arc through neutral zone (around cone)
    arc_points = [
        (-20, -25),
        (-10, -20),
        (-5, -10),
        (-8, 0),
        (-15, 5),
        (-25, 8),
        (-35, 5)
    ]
    for i in range(len(arc_points) - 1):
        label = 'Around cone' if i == 2 else ''
        movements.append(Movement(
            type='carry',
            from_pos={'x': arc_points[i][0], 'y': arc_points[i][1]},
            to_pos={'x': arc_points[i+1][0], 'y': arc_points[i+1][1]},
            style='dashed' if i < 5 else 'solid',
            with_puck=True,
            label=label
        ))

    # 4. Enter zone toward blue line area
    movements.append(Movement(type='carry', from_pos={'x': -35, 'y': 5},
                             to_pos={'x': -45, 'y': -2}, style='solid', with_puck=True, label=''))

    # DEFENSIVE PATH
    # 1. Cross ice from top to bottom boards, heading toward pylon
    movements.append(Movement(type='skate', from_pos={'x': -75, 'y': 38},
                             to_pos={'x': -53, 'y': -20}, style='solid', label='Cross ice'))

    # 2. Arc around the pylon
    movements.append(Movement(type='skate', from_pos={'x': -53, 'y': -20},
                             to_pos={'x': -50, 'y': -25}, style='dashed', label=''))
    movements.append(Movement(type='skate', from_pos={'x': -50, 'y': -25},
                             to_pos={'x': -47, 'y': -23}, style='dashed', label='Around pylon'))
    movements.append(Movement(type='skate', from_pos={'x': -47, 'y': -23},
                             to_pos={'x': -46, 'y': -20}, style='dashed', label=''))

    # 3. Angle back toward intercept point at blue line area
    movements.append(Movement(type='skate', from_pos={'x': -46, 'y': -20},
                             to_pos={'x': -45, 'y': -5}, style='solid', label='Angle to intercept'))

    # 4. Defensive engagement at blue line
    movements.append(Movement(type='pressure', from_pos={'x': -45, 'y': -5},
                             to_pos={'x': -45, 'y': -2}, style='solid', label='Defend at blue line'))

    # Add all movements to spec
    spec.movements = movements

    # Build the diagram
    builder = DiagramBuilder()
    
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill2_backcheck_angling_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    
    # Save the spec
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Diagram created: {result}')
    print(f'Spec saved: {spec_path}')
    
    return result, spec_path


if __name__ == "__main__":
    create_drill2_diagram()