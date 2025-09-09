#!/usr/bin/env python3
"""
Drill 1: Warm-Up - Crossovers & Pass
Final iteration (16) from August 27, 2025 practice

This drill features:
- Two groups starting from opposite corners
- Counterclockwise crossovers around center circle
- Offset entry angles (315° and 135°) for visual clarity
- Pass at blue line, receive at top of circle, shoot at hashmarks
- Straight line trajectory from circle exit to shooting position
"""

import sys
import numpy as np
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation


def generate_arc_points(center_x, center_y, radius, start_angle, end_angle, num_points=15):
    """
    Generate points along a circle arc - ensuring counterclockwise direction.
    
    Key learning from iterations: If end_angle is less than start_angle, 
    we must add 360° to ensure counterclockwise movement.
    """
    if end_angle <= start_angle:
        end_angle += 360
    angles = np.linspace(np.radians(start_angle), np.radians(end_angle), num_points)
    x_points = center_x + radius * np.cos(angles)
    y_points = center_y + radius * np.sin(angles)
    return [(float(x), float(y)) for x, y in zip(x_points, y_points)]


def create_drill1_diagram(output_path=None):
    """
    Create the Drill 1 diagram with all the refinements from 16 iterations.
    """
    # Create the diagram specification
    spec = DiagramSpec(
        title='Drill 1: Warm-Up - Crossovers & Pass',
        rink={'view': 'full', 'show_zones': True, 'show_faceoff_dots': True},
        players=[
            # Group 1 queue - positioned off boards for visibility
            Player(type='forward', position='X1', coordinates={'x': -20, 'y': -38}, 
                   team='home', has_puck=True, label='X1'),
            Player(type='forward', position='X', coordinates={'x': -25, 'y': -38}, 
                   team='home', label='X'),
            Player(type='forward', position='X', coordinates={'x': -30, 'y': -38}, 
                   team='home', label='X'),

            # Group 2 queue - positioned off boards for visibility
            Player(type='forward', position='X2', coordinates={'x': 20, 'y': 38}, 
                   team='home', has_puck=True, label='X2'),
            Player(type='forward', position='X', coordinates={'x': 25, 'y': 38}, 
                   team='home', label='X'),
            Player(type='forward', position='X', coordinates={'x': 30, 'y': 38}, 
                   team='home', label='X'),

            # Coaches positioned near boards
            Player(type='coach', position='C1', coordinates={'x': -69, 'y': 35}, 
                   team='home', label='C1'),
            Player(type='coach', position='C2', coordinates={'x': 69, 'y': -35}, 
                   team='home', label='C2'),

            # Goalies in crease
            Player(type='goalie', position='G1', coordinates={'x': -83, 'y': 0}, 
                   team='home', label='G1'),
            Player(type='goalie', position='G2', coordinates={'x': 83, 'y': 0}, 
                   team='home', label='G2')
        ],
        movements=[],
        zones=[
            # Highlight center circle for reference
            Zone(type='coverage', shape='circle', 
                 bounds={'x': 0, 'y': 0, 'radius': 15}, 
                 team='home', opacity=0.15, color='yellow', label='')
        ],
        annotations=[
            Annotation(text='Key Points:', position={'x': 0, 'y': -35}, 
                      size='medium', style='bold'),
            Annotation(text='• Counterclockwise crossovers around center circle', 
                      position={'x': 0, 'y': -38}, size='small', style='normal'),
            Annotation(text='• Offset entry angles for path clarity', 
                      position={'x': 0, 'y': -40}, size='small', style='normal'),
            Annotation(text='• Pass/receive along straight trajectory to slot', 
                      position={'x': 0, 'y': -42}, size='small', style='normal'),
            Annotation(text='Groups alternate - continuous flow', 
                      position={'x': 0, 'y': 38}, size='small', style='normal')
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'age_group': 'U11',
            'skill_level': 'intermediate',
            'drill_type': 'warm-up',
            'iteration': 16,
            'final': True
        }
    )

    # Create movements
    movements = []
    arc_radius = 17  # Outside the 15ft center circle

    # === X1 PATH (Left side) ===
    # 1. Approach to circle
    entry_angle = 315  # Offset entry for visual clarity
    entry_x = arc_radius * np.cos(np.radians(entry_angle))
    entry_y = arc_radius * np.sin(np.radians(entry_angle))
    movements.append(Movement(type='skate', from_pos={'x': -20, 'y': -38},
                              to_pos={'x': entry_x, 'y': entry_y}, 
                              style='solid', label=''))

    # 2. Counterclockwise arc around circle (135 degrees)
    exit_angle = 90  # Exit at top
    arc_points = generate_arc_points(0, 0, arc_radius, 315, exit_angle, 10)
    for i in range(len(arc_points) - 1):
        label = 'Crossovers' if i == 4 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': arc_points[i][0], 'y': arc_points[i][1]},
            to_pos={'x': arc_points[i+1][0], 'y': arc_points[i+1][1]},
            style='dashed',
            label=label
        ))

    # 3. Calculate straight trajectory to shooting position
    exit_x = arc_radius * np.cos(np.radians(90))  # ~0
    exit_y = arc_radius * np.sin(np.radians(90))  # ~17
    shoot_x = -75  # Shooting position (hashmarks)
    shoot_y = 5    # Mid-slot

    # Points along trajectory for pass/receive
    pass_x = exit_x + (shoot_x - exit_x) * 0.33  # Blue line area
    pass_y = exit_y + (shoot_y - exit_y) * 0.33
    receive_x = exit_x + (shoot_x - exit_x) * 0.66  # Top of circle
    receive_y = exit_y + (shoot_y - exit_y) * 0.66

    # 4-9. Complete the play sequence
    movements.append(Movement(type='skate', from_pos={'x': exit_x, 'y': exit_y},
                              to_pos={'x': pass_x, 'y': pass_y}, style='solid'))
    movements.append(Movement(type='pass', from_pos={'x': pass_x, 'y': pass_y},
                              to_pos={'x': -69, 'y': 35}, style='dotted', label='Pass'))
    movements.append(Movement(type='skate', from_pos={'x': pass_x, 'y': pass_y},
                              to_pos={'x': receive_x, 'y': receive_y}, style='solid'))
    movements.append(Movement(type='pass', from_pos={'x': -69, 'y': 35},
                              to_pos={'x': receive_x, 'y': receive_y}, 
                              style='dotted', label='Receive'))
    movements.append(Movement(type='carry', from_pos={'x': receive_x, 'y': receive_y},
                              to_pos={'x': shoot_x, 'y': shoot_y}, 
                              style='solid', with_puck=True))
    movements.append(Movement(type='shot', from_pos={'x': shoot_x, 'y': shoot_y},
                              to_pos={'x': -83, 'y': 0}, style='dashed', label='Shot'))

    # === X2 PATH (Right side - mirror) ===
    # 1. Approach to circle
    entry_angle = 135  # Offset entry for visual clarity
    entry_x = arc_radius * np.cos(np.radians(entry_angle))
    entry_y = arc_radius * np.sin(np.radians(entry_angle))
    movements.append(Movement(type='skate', from_pos={'x': 20, 'y': 38},
                              to_pos={'x': entry_x, 'y': entry_y}, 
                              style='solid', label=''))

    # 2. Counterclockwise arc around circle (135 degrees)
    exit_angle = 270  # Exit at bottom
    arc_points = generate_arc_points(0, 0, arc_radius, 135, exit_angle, 10)
    for i in range(len(arc_points) - 1):
        label = 'Crossovers' if i == 4 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': arc_points[i][0], 'y': arc_points[i][1]},
            to_pos={'x': arc_points[i+1][0], 'y': arc_points[i+1][1]},
            style='dashed',
            label=label
        ))

    # 3. Calculate straight trajectory to shooting position
    exit_x = arc_radius * np.cos(np.radians(270))  # ~0
    exit_y = arc_radius * np.sin(np.radians(270))  # ~-17
    shoot_x = 75   # Shooting position (hashmarks)
    shoot_y = -5   # Mid-slot

    # Points along trajectory for pass/receive
    pass_x = exit_x + (shoot_x - exit_x) * 0.33  # Blue line area
    pass_y = exit_y + (shoot_y - exit_y) * 0.33
    receive_x = exit_x + (shoot_x - exit_x) * 0.66  # Top of circle
    receive_y = exit_y + (shoot_y - exit_y) * 0.66

    # 4-9. Complete the play sequence
    movements.append(Movement(type='skate', from_pos={'x': exit_x, 'y': exit_y},
                              to_pos={'x': pass_x, 'y': pass_y}, style='solid'))
    movements.append(Movement(type='pass', from_pos={'x': pass_x, 'y': pass_y},
                              to_pos={'x': 69, 'y': -35}, style='dotted', label='Pass'))
    movements.append(Movement(type='skate', from_pos={'x': pass_x, 'y': pass_y},
                              to_pos={'x': receive_x, 'y': receive_y}, style='solid'))
    movements.append(Movement(type='pass', from_pos={'x': 69, 'y': -35},
                              to_pos={'x': receive_x, 'y': receive_y}, 
                              style='dotted', label='Receive'))
    movements.append(Movement(type='carry', from_pos={'x': receive_x, 'y': receive_y},
                              to_pos={'x': shoot_x, 'y': shoot_y}, 
                              style='solid', with_puck=True))
    movements.append(Movement(type='shot', from_pos={'x': shoot_x, 'y': shoot_y},
                              to_pos={'x': 83, 'y': 0}, style='dashed', label='Shot'))

    # Add all movements to spec
    spec.movements = movements

    # Build the diagram
    builder = DiagramBuilder()
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'outputs/drill1_crossovers_pass_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    
    # Save the spec
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Diagram created: {result}')
    print(f'Spec saved: {spec_path}')
    
    return result, spec_path


if __name__ == "__main__":
    # Generate the diagram when run directly
    create_drill1_diagram()