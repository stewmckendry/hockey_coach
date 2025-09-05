#!/usr/bin/env python
"""
Drill 3: 3v2 Breakout & Breakin
Two-part drill for practicing breakout and attacking scenarios
Created: 2025-08-27

Part 1 - Break Out:
- Coach dumps puck into zone
- Defense retrieves and breaks out
- Forwards support and receive passes

Part 2 - Break In:
- After getting puck back from coach
- 3 forwards attack 2 defense
- Offensive zone entry and scoring chance
"""

import sys
import numpy as np
from datetime import datetime
from pathlib import Path
sys.path.append('..')

from hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation
from drill_utilities import generate_arc_points, STANDARD_POSITIONS, Z_ORDER

def create_drill3_part1_diagram(output_path=None):
    """Create Drill 3 Part 1: Break Out diagram"""
    
    spec = DiagramSpec(
        title='Drill 3 Part 1: Break Out',
        rink={'view': 'full', 'show_zones': True, 'show_faceoff_dots': True},
        players=[
            # 3 Forwards on red line (SWAPPED LW and RW positions)
            Player(type='forward', position='RW', coordinates={'x': 0, 'y': -22.5},
                   team='home', has_puck=False, label='RW'),
            Player(type='forward', position='C', coordinates={'x': 0, 'y': 0},
                   team='home', has_puck=False, label='C'),
            Player(type='forward', position='LW', coordinates={'x': 0, 'y': 22.5},
                   team='home', has_puck=False, label='LW'),
            
            # 2 Defense on blue line (left zone)
            Player(type='defense', position='LD', coordinates={'x': -25, 'y': -15},
                   team='home', has_puck=False, label='LD'),
            Player(type='defense', position='RD', coordinates={'x': -25, 'y': 15},
                   team='home', has_puck=False, label='RD'),
            
            # Coach on opposite blue line
            Player(type='coach', position='Coach', coordinates={'x': 25, 'y': 0},
                   team='neutral', has_puck=True, label='C'),
            
            # Goalie
            Player(type='goalie', position='G', coordinates={'x': -83, 'y': 0},
                   team='home', label='G'),
                   
            # Puck in LEFT CORNER (top of diagram)
            Player(type='puck', position='Puck', coordinates={'x': -85, 'y': 35},
                   team='neutral', has_puck=False),
        ],
        movements=[],
        zones=[
            # Defensive zone highlight
            Zone(type='coverage', shape='rectangle',
                 bounds={'x': -89, 'y': -42.5, 'width': 64, 'height': 85},
                 team='home', opacity=0.03, color='lightblue', label='')
        ],
        annotations=[
            Annotation(text='PART 1 - BREAK OUT', position={'x': 0, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='Setup:', position={'x': -60, 'y': 35},
                      size='medium', style='bold'),
            Annotation(text='• 3 forwards on red line', position={'x': -60, 'y': 32},
                      size='small', style='normal'),
            Annotation(text='• 2 defense on blue line', position={'x': -60, 'y': 30},
                      size='small', style='normal'),
            Annotation(text='• Coach dumps puck', position={'x': -60, 'y': 28},
                      size='small', style='normal'),
            
            Annotation(text='Flow:', position={'x': 60, 'y': 35},
                      size='medium', style='bold'),
            Annotation(text='• LD retrieves puck', position={'x': 60, 'y': 32},
                      size='small', style='normal'),
            Annotation(text='• RD goes to net front', position={'x': 60, 'y': 30},
                      size='small', style='normal'),
            Annotation(text='• LW supports at hashmarks', position={'x': 60, 'y': 28},
                      size='small', style='normal'),
            Annotation(text='• C curls for support', position={'x': 60, 'y': 26},
                      size='small', style='normal'),
            Annotation(text='• RW stays high/middle', position={'x': 60, 'y': 24},
                      size='small', style='normal'),
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'age_group': 'U11',
            'skill_level': 'intermediate',
            'drill_type': 'systems'
        }
    )

    # Create movements for Part 1
    movements = []

    # 1. Coach dumps puck into corner
    movements.append(Movement(type='pass', from_pos={'x': 25, 'y': 0},
                             to_pos={'x': -85, 'y': 35}, style='dotted', label='Dump'))

    # 2. Players skate into zone
    # Left Defense goes STRAIGHT to retrieve puck in corner
    movements.append(Movement(type='skate', from_pos={'x': -25, 'y': -15},
                             to_pos={'x': -85, 'y': 33}, style='solid', label='Retrieve'))

    # Right Defense goes STRAIGHT to net front
    movements.append(Movement(type='skate', from_pos={'x': -25, 'y': 15},
                             to_pos={'x': -78, 'y': 5}, style='solid', label='Net front'))

    # Left Wing skates from position to hashmarks on boards (upper/left side)
    movements.append(Movement(type='skate', from_pos={'x': 0, 'y': 22.5},
                             to_pos={'x': -69, 'y': 38}, style='solid', label='To boards'))

    # Centre skates down and curls around left (upper) faceoff dot
    # Small arc around the dot at (-69, 22.5)
    movements.append(Movement(type='skate', from_pos={'x': 0, 'y': 0},
                             to_pos={'x': -50, 'y': 15}, style='solid', label=''))
    
    # Arc around the upper faceoff dot
    arc_points = generate_arc_points(-69, 22.5, 8, 0, 180, 5)
    for i in range(len(arc_points) - 1):
        label = 'Curl' if i == 2 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': arc_points[i][0], 'y': arc_points[i][1]},
            to_pos={'x': arc_points[i+1][0], 'y': arc_points[i+1][1]},
            style='dashed',
            label=label
        ))

    # Right Wing skates down to top of circle and curls to middle
    movements.append(Movement(type='skate', from_pos={'x': 0, 'y': -22.5},
                             to_pos={'x': -52, 'y': -22.5}, style='solid', label=''))
    
    # Small arc to middle ice
    movements.append(Movement(type='skate', from_pos={'x': -52, 'y': -22.5},
                             to_pos={'x': -45, 'y': -10}, style='dashed', label=''))
    movements.append(Movement(type='skate', from_pos={'x': -45, 'y': -10},
                             to_pos={'x': -40, 'y': 0}, style='dashed', label='Middle'))

    # 3. Breakout sequence
    # LD passes to LW at boards
    movements.append(Movement(type='pass', from_pos={'x': -85, 'y': 33},
                             to_pos={'x': -69, 'y': 38}, style='dotted', label='Pass'))

    # LW passes to Centre who has curled
    movements.append(Movement(type='pass', from_pos={'x': -69, 'y': 38},
                             to_pos={'x': -77, 'y': 22.5}, style='dotted', label=''))

    # 4. Move out of defensive zone
    # Centre carries puck up ice
    movements.append(Movement(type='carry', from_pos={'x': -77, 'y': 22.5},
                             to_pos={'x': -10, 'y': 10}, style='solid', with_puck=True, label='Carry'))

    # Forwards move into neutral zone
    movements.append(Movement(type='skate', from_pos={'x': -69, 'y': 38},
                             to_pos={'x': -15, 'y': 20}, style='solid', label=''))
    
    movements.append(Movement(type='skate', from_pos={'x': -40, 'y': 0},
                             to_pos={'x': -5, 'y': -5}, style='solid', label=''))

    # 5. Pass to coach and receive back
    movements.append(Movement(type='pass', from_pos={'x': -10, 'y': 10},
                             to_pos={'x': 25, 'y': 0}, style='dotted', label='Pass to coach'))

    movements.append(Movement(type='pass', from_pos={'x': 25, 'y': 0},
                             to_pos={'x': 5, 'y': 5}, style='dotted', label='Return pass'))

    # Add all movements to spec
    spec.movements = movements

    # Build the diagram
    builder = DiagramBuilder()
    
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_part1_breakout_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    
    # Save the spec
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Part 1 Diagram created: {result}')
    print(f'Part 1 Spec saved: {spec_path}')
    
    return result, spec_path


def create_drill3_part2_diagram(output_path=None):
    """Create Drill 3 Part 2: Break In (3v2) diagram"""
    
    spec = DiagramSpec(
        title='Drill 3 Part 2: Break In (3v2)',
        rink={'view': 'full', 'show_zones': True, 'show_faceoff_dots': True},
        players=[
            # 3 Forwards in neutral zone (after receiving puck back)
            Player(type='forward', position='LW', coordinates={'x': 5, 'y': -20},
                   team='home', has_puck=False, label='LW'),
            Player(type='forward', position='C', coordinates={'x': 5, 'y': -5},
                   team='home', has_puck=True, label='C'),
            Player(type='forward', position='RW', coordinates={'x': 5, 'y': 15},
                   team='home', has_puck=False, label='RW'),
            
            # 2 Defense at defensive positions (right zone)
            Player(type='defense', position='LD', coordinates={'x': 50, 'y': -15},
                   team='away', has_puck=False, label='D'),
            Player(type='defense', position='RD', coordinates={'x': 50, 'y': 15},
                   team='away', has_puck=False, label='D'),
            
            # Goalie in right net
            Player(type='goalie', position='G', coordinates={'x': 83, 'y': 0},
                   team='away', label='G'),
        ],
        movements=[],
        zones=[
            # Offensive zone highlight (right side)
            Zone(type='coverage', shape='rectangle',
                 bounds={'x': 25, 'y': -42.5, 'width': 64, 'height': 85},
                 team='away', opacity=0.03, color='lightcoral', label='')
        ],
        annotations=[
            Annotation(text='PART 2 - BREAK IN (3v2)', position={'x': 0, 'y': 38},
                      size='large', style='bold'),
            
            Annotation(text='Sequence:', position={'x': -60, 'y': 35},
                      size='medium', style='bold'),
            Annotation(text='1. Forwards enter zone together', position={'x': -60, 'y': 32},
                      size='small', style='normal'),
            Annotation(text='2. C passes to LW', position={'x': -60, 'y': 30},
                      size='small', style='normal'),
            Annotation(text='3. LW wide / C net / RW high', position={'x': -60, 'y': 28},
                      size='small', style='normal'),
            Annotation(text='4. Defense reacts', position={'x': -60, 'y': 26},
                      size='small', style='normal'),
            Annotation(text='5. Multiple options', position={'x': -60, 'y': 24},
                      size='small', style='normal'),
            
            Annotation(text='Options:', position={'x': 60, 'y': 35},
                      size='medium', style='bold'),
            Annotation(text='A: Shot on goal', position={'x': 60, 'y': 32},
                      size='small', style='normal'),
            Annotation(text='B: Pass to high forward', position={'x': 60, 'y': 30},
                      size='small', style='normal'),
            Annotation(text='C: Pass to net-front', position={'x': 60, 'y': 28},
                      size='small', style='normal'),
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'age_group': 'U11',
            'skill_level': 'intermediate',
            'drill_type': 'systems'
        }
    )

    # Create movements for Part 2 with clearer sequence
    movements = []

    # STEP 1: Initial entry - all three forwards advance together
    movements.append(Movement(type='carry', from_pos={'x': 5, 'y': -5},
                             to_pos={'x': 35, 'y': -8}, style='solid', with_puck=True, label='1. Entry'))
    
    movements.append(Movement(type='skate', from_pos={'x': 5, 'y': -20},
                             to_pos={'x': 35, 'y': -25}, style='solid', label=''))
    
    movements.append(Movement(type='skate', from_pos={'x': 5, 'y': 15},
                             to_pos={'x': 35, 'y': 15}, style='solid', label=''))

    # STEP 2: Centre passes to LW who goes wide
    movements.append(Movement(type='pass', from_pos={'x': 35, 'y': -8},
                             to_pos={'x': 35, 'y': -25}, style='dotted', label='2. Pass'))

    # STEP 3: Three-pronged attack
    # LW carries wide
    movements.append(Movement(type='carry', from_pos={'x': 35, 'y': -25},
                             to_pos={'x': 65, 'y': -32}, style='solid', with_puck=True, label='3. Go wide'))
    
    # Centre drives to net
    movements.append(Movement(type='skate', from_pos={'x': 35, 'y': -8},
                             to_pos={'x': 73, 'y': -3}, style='solid', label='3. Drive net'))

    # RW stays high for support
    movements.append(Movement(type='skate', from_pos={'x': 35, 'y': 15},
                             to_pos={'x': 50, 'y': 10}, style='solid', label='3. Stay high'))

    # STEP 4: Defense reactions
    # Left D angles to pressure puck carrier
    movements.append(Movement(type='pressure', from_pos={'x': 50, 'y': -15},
                             to_pos={'x': 62, 'y': -28}, style='solid', label='4. Angle'))

    # Right D protects net front
    movements.append(Movement(type='skate', from_pos={'x': 50, 'y': 15},
                             to_pos={'x': 75, 'y': 5}, style='solid', label='4. Net front'))

    # STEP 5: Offensive options (shown with different styles)
    # Option A: Shot
    movements.append(Movement(type='shot', from_pos={'x': 65, 'y': -32},
                             to_pos={'x': 83, 'y': 0}, style='dashed', label='5A. Shot'))

    # Option B: Pass to high forward
    movements.append(Movement(type='pass', from_pos={'x': 65, 'y': -32},
                             to_pos={'x': 50, 'y': 10}, style='dotted', label='5B. Pass high'))

    # Option C: Pass to net-front Centre
    movements.append(Movement(type='pass', from_pos={'x': 65, 'y': -32},
                             to_pos={'x': 73, 'y': -3}, style='dotted', label='5C. Pass net'))

    # Add all movements to spec
    spec.movements = movements

    # Build the diagram
    builder = DiagramBuilder()
    
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_part2_breakin_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    
    # Save the spec
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Part 2 Diagram created: {result}')
    print(f'Part 2 Spec saved: {spec_path}')
    
    return result, spec_path


def create_both_diagrams():
    """Create both Part 1 and Part 2 diagrams"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create Part 1
    part1_path = f'../../outputs/drill3_part1_breakout_{timestamp}.png'
    part1_result, part1_spec = create_drill3_part1_diagram(part1_path)
    
    # Create Part 2
    part2_path = f'../../outputs/drill3_part2_breakin_{timestamp}.png'
    part2_result, part2_spec = create_drill3_part2_diagram(part2_path)
    
    return (part1_result, part1_spec), (part2_result, part2_spec)


if __name__ == "__main__":
    # Create both diagrams
    create_both_diagrams()