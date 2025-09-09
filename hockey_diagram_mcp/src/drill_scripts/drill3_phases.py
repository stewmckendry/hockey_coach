#!/usr/bin/env python
"""
Drill 3: 3v2 Breakout & Breakin - PHASE-BASED VERSION
Cleaner diagrams with natural curved movements
Created: 2025-08-27 (Iteration 3)

Breaking complex drills into digestible phases with smooth, natural hockey movements.
"""

import sys
import numpy as np
from datetime import datetime
from pathlib import Path
sys.path.append('..')

from hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation
from drill_utilities import generate_arc_points, STANDARD_POSITIONS, Z_ORDER

def create_smooth_path(start, waypoints, end):
    """Create a smooth curved path through waypoints."""
    all_points = [start] + waypoints + [end]
    return all_points  # Will be used by _draw_curved_path

def create_drill3_part1_phase1(output_path=None):
    """Part 1 Phase 1: Dump-in and Retrieval"""
    
    spec = DiagramSpec(
        title='Drill 3 Part 1: Breakout - Phase 1 (Dump & Retrieve)',
        rink={'view': 'defensive'},  # Focus on defensive zone
        players=[
            # Starting positions
            Player(type='forward', position='RW', coordinates={'x': -25, 'y': -22.5},
                   team='home', has_puck=False, label='RW'),
            Player(type='forward', position='C', coordinates={'x': -25, 'y': 0},
                   team='home', has_puck=False, label='C'),
            Player(type='forward', position='LW', coordinates={'x': -25, 'y': 22.5},
                   team='home', has_puck=False, label='LW'),
            
            Player(type='defense', position='LD', coordinates={'x': -25, 'y': -15},
                   team='home', has_puck=False, label='LD'),
            Player(type='defense', position='RD', coordinates={'x': -25, 'y': 15},
                   team='home', has_puck=False, label='RD'),
            
            Player(type='coach', position='Coach', coordinates={'x': -25, 'y': 35},
                   team='neutral', has_puck=True, label='C'),
            
            Player(type='goalie', position='G', coordinates={'x': -83, 'y': 0},
                   team='home', label='G'),
                   
            # Puck destination
            Player(type='puck', position='Puck', coordinates={'x': -85, 'y': 35},
                   team='neutral', has_puck=False),
        ],
        movements=[],
        zones=[],
        annotations=[
            Annotation(text='PHASE 1: Dump & Retrieve', position={'x': -62.5, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='Coach dumps puck • LD retrieves • RD to net', position={'x': -62.5, 'y': 35},
                      size='small', style='normal'),
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'phase': 1
        }
    )

    # Create smooth movements
    movements = []
    
    # Coach dumps puck (simple arc)
    movements.append(Movement(type='pass', from_pos={'x': -25, 'y': 35},
                             to_pos={'x': -85, 'y': 35}, style='dotted', label='Dump'))
    
    # LD smooth curve to puck
    builder = DiagramBuilder()
    path_points = [
        (-25, -15),   # Start
        (-45, -5),    # Waypoint 1
        (-65, 10),    # Waypoint 2  
        (-85, 33)     # End near puck
    ]
    # We'll use multiple movements to simulate the curve
    for i in range(len(path_points) - 1):
        label = 'Retrieve' if i == 1 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': path_points[i][0], 'y': path_points[i][1]},
            to_pos={'x': path_points[i+1][0], 'y': path_points[i+1][1]},
            style='solid',
            label=label
        ))
    
    # RD smooth curve to net front
    net_path = [
        (-25, 15),    # Start
        (-45, 12),    # Waypoint
        (-65, 8),     # Waypoint
        (-78, 5)      # Net front
    ]
    for i in range(len(net_path) - 1):
        label = 'Net front' if i == 1 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': net_path[i][0], 'y': net_path[i][1]},
            to_pos={'x': net_path[i+1][0], 'y': net_path[i+1][1]},
            style='solid',
            label=label
        ))

    spec.movements = movements
    
    builder = DiagramBuilder()
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_part1_phase1_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Phase 1 created: {result}')
    return result, spec_path


def create_drill3_part1_phase2(output_path=None):
    """Part 1 Phase 2: Support and Breakout Pass"""
    
    spec = DiagramSpec(
        title='Drill 3 Part 1: Breakout - Phase 2 (Support & Pass)',
        rink={'view': 'defensive'},
        players=[
            # Positions after Phase 1
            Player(type='defense', position='LD', coordinates={'x': -85, 'y': 33},
                   team='home', has_puck=True, label='LD'),
            Player(type='defense', position='RD', coordinates={'x': -78, 'y': 5},
                   team='home', has_puck=False, label='RD'),
            
            # Forwards moving into support positions
            Player(type='forward', position='LW', coordinates={'x': -25, 'y': 22.5},
                   team='home', has_puck=False, label='LW'),
            Player(type='forward', position='C', coordinates={'x': -25, 'y': 0},
                   team='home', has_puck=False, label='C'),
            Player(type='forward', position='RW', coordinates={'x': -25, 'y': -22.5},
                   team='home', has_puck=False, label='RW'),
            
            Player(type='goalie', position='G', coordinates={'x': -83, 'y': 0},
                   team='home', label='G'),
        ],
        movements=[],
        zones=[],
        annotations=[
            Annotation(text='PHASE 2: Support & Pass', position={'x': -62.5, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='LW to boards • C curls around dot • RW to middle', position={'x': -62.5, 'y': 35},
                      size='small', style='normal'),
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'phase': 2
        }
    )

    movements = []
    
    # LW curves to boards/hashmarks
    lw_path = [
        (-25, 22.5),   # Start
        (-45, 28),     # Waypoint
        (-60, 35),     # Waypoint
        (-69, 38)      # Boards position
    ]
    for i in range(len(lw_path) - 1):
        label = 'Support' if i == 1 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': lw_path[i][0], 'y': lw_path[i][1]},
            to_pos={'x': lw_path[i+1][0], 'y': lw_path[i+1][1]},
            style='solid',
            label=label
        ))
    
    # Centre curls around upper faceoff dot
    # Create a smooth arc around the dot at (-69, 22.5)
    c_path = [
        (-25, 0),      # Start
        (-45, 10),     # Approach
        (-60, 18),     # Enter curve
        (-69, 22.5),   # Around dot
        (-75, 20),     # Complete curl
        (-77, 22.5)    # Support position
    ]
    for i in range(len(c_path) - 1):
        label = 'Curl' if i == 3 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': c_path[i][0], 'y': c_path[i][1]},
            to_pos={'x': c_path[i+1][0], 'y': c_path[i+1][1]},
            style='dashed' if i >= 2 else 'solid',
            label=label
        ))
    
    # RW curves to middle ice
    rw_path = [
        (-25, -22.5),  # Start
        (-45, -20),    # Waypoint
        (-55, -10),    # Waypoint
        (-45, 0)       # Middle ice
    ]
    for i in range(len(rw_path) - 1):
        label = 'Middle' if i == 2 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': rw_path[i][0], 'y': rw_path[i][1]},
            to_pos={'x': rw_path[i+1][0], 'y': rw_path[i+1][1]},
            style='dashed' if i >= 1 else 'solid',
            label=label
        ))
    
    # LD passes to LW at boards
    movements.append(Movement(type='pass', from_pos={'x': -85, 'y': 33},
                             to_pos={'x': -69, 'y': 38}, style='dotted', label='Pass'))

    spec.movements = movements
    
    builder = DiagramBuilder()
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_part1_phase2_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Phase 2 created: {result}')
    return result, spec_path


def create_drill3_part1_phase3(output_path=None):
    """Part 1 Phase 3: Exit to Neutral Zone"""
    
    spec = DiagramSpec(
        title='Drill 3 Part 1: Breakout - Phase 3 (Exit Zone)',
        rink={'view': 'full'},  # Need to see neutral zone
        players=[
            # Positions after Phase 2
            Player(type='forward', position='LW', coordinates={'x': -69, 'y': 38},
                   team='home', has_puck=True, label='LW'),
            Player(type='forward', position='C', coordinates={'x': -77, 'y': 22.5},
                   team='home', has_puck=False, label='C'),
            Player(type='forward', position='RW', coordinates={'x': -45, 'y': 0},
                   team='home', has_puck=False, label='RW'),
            
            Player(type='coach', position='Coach', coordinates={'x': 25, 'y': 0},
                   team='neutral', has_puck=False, label='C'),
            
            Player(type='goalie', position='G', coordinates={'x': -83, 'y': 0},
                   team='home', label='G'),
        ],
        movements=[],
        zones=[],
        annotations=[
            Annotation(text='PHASE 3: Exit Zone', position={'x': 0, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='LW passes to C • Team exits zone • Pass to coach & return', position={'x': 0, 'y': 35},
                      size='small', style='normal'),
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'phase': 3
        }
    )

    movements = []
    
    # LW to Centre pass
    movements.append(Movement(type='pass', from_pos={'x': -69, 'y': 38},
                             to_pos={'x': -77, 'y': 22.5}, style='dotted', label=''))
    
    # Centre carries out with smooth curve
    c_carry = [
        (-77, 22.5),   # Start
        (-50, 20),     # Waypoint
        (-25, 15),     # Blue line
        (-5, 10),      # Neutral zone
        (10, 5)        # Near center
    ]
    for i in range(len(c_carry) - 1):
        label = 'Carry out' if i == 2 else ''
        movements.append(Movement(
            type='carry',
            from_pos={'x': c_carry[i][0], 'y': c_carry[i][1]},
            to_pos={'x': c_carry[i+1][0], 'y': c_carry[i+1][1]},
            style='solid',
            with_puck=True,
            label=label
        ))
    
    # Support players exit with curves
    lw_exit = [
        (-69, 38),     # Start
        (-45, 30),     # Waypoint
        (-20, 25),     # Blue line
        (0, 20)        # Neutral zone
    ]
    for i in range(len(lw_exit) - 1):
        movements.append(Movement(
            type='skate',
            from_pos={'x': lw_exit[i][0], 'y': lw_exit[i][1]},
            to_pos={'x': lw_exit[i+1][0], 'y': lw_exit[i+1][1]},
            style='solid',
            label=''
        ))
    
    rw_exit = [
        (-45, 0),      # Start
        (-25, -5),     # Waypoint
        (-5, -8),      # Blue line
        (10, -10)      # Neutral zone
    ]
    for i in range(len(rw_exit) - 1):
        movements.append(Movement(
            type='skate',
            from_pos={'x': rw_exit[i][0], 'y': rw_exit[i][1]},
            to_pos={'x': rw_exit[i+1][0], 'y': rw_exit[i+1][1]},
            style='solid',
            label=''
        ))
    
    # Pass to coach and return
    movements.append(Movement(type='pass', from_pos={'x': 10, 'y': 5},
                             to_pos={'x': 25, 'y': 0}, style='dotted', label='Pass'))
    movements.append(Movement(type='pass', from_pos={'x': 25, 'y': 0},
                             to_pos={'x': 15, 'y': 5}, style='dotted', label='Return'))

    spec.movements = movements
    
    builder = DiagramBuilder()
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_part1_phase3_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Phase 3 created: {result}')
    return result, spec_path


def create_drill3_part2_phase1(output_path=None):
    """Part 2 Phase 1: Zone Entry"""
    
    spec = DiagramSpec(
        title='Drill 3 Part 2: 3v2 - Phase 1 (Entry)',
        rink={'view': 'offensive'},
        players=[
            # Starting positions in neutral zone
            Player(type='forward', position='LW', coordinates={'x': 25, 'y': -20},
                   team='home', has_puck=False, label='LW'),
            Player(type='forward', position='C', coordinates={'x': 25, 'y': 0},
                   team='home', has_puck=True, label='C'),
            Player(type='forward', position='RW', coordinates={'x': 25, 'y': 20},
                   team='home', has_puck=False, label='RW'),
            
            # Defense in position
            Player(type='defense', position='LD', coordinates={'x': 50, 'y': -15},
                   team='away', has_puck=False, label='D'),
            Player(type='defense', position='RD', coordinates={'x': 50, 'y': 15},
                   team='away', has_puck=False, label='D'),
            
            Player(type='goalie', position='G', coordinates={'x': 83, 'y': 0},
                   team='away', label='G'),
        ],
        movements=[],
        zones=[],
        annotations=[
            Annotation(text='PHASE 1: Zone Entry', position={'x': 62.5, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='3 forwards enter together • C carries then passes to LW', position={'x': 62.5, 'y': 35},
                      size='small', style='normal'),
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'phase': 1
        }
    )

    movements = []
    
    # All three forwards enter with smooth curves
    # Centre with puck
    c_entry = [
        (25, 0),       # Start
        (35, -2),      # Slight angle
        (45, -5),      # Continue
        (55, -8)       # Entry point
    ]
    for i in range(len(c_entry) - 1):
        label = 'Entry' if i == 1 else ''
        movements.append(Movement(
            type='carry',
            from_pos={'x': c_entry[i][0], 'y': c_entry[i][1]},
            to_pos={'x': c_entry[i+1][0], 'y': c_entry[i+1][1]},
            style='solid',
            with_puck=True,
            label=label
        ))
    
    # LW enters wide
    lw_entry = [
        (25, -20),     # Start
        (35, -22),     # Wide angle
        (45, -25),     # Continue wide
        (55, -28)      # Wide position
    ]
    for i in range(len(lw_entry) - 1):
        movements.append(Movement(
            type='skate',
            from_pos={'x': lw_entry[i][0], 'y': lw_entry[i][1]},
            to_pos={'x': lw_entry[i+1][0], 'y': lw_entry[i+1][1]},
            style='solid',
            label=''
        ))
    
    # RW enters high
    rw_entry = [
        (25, 20),      # Start
        (35, 18),      # Slight in
        (45, 15),      # Continue
        (55, 12)       # High position
    ]
    for i in range(len(rw_entry) - 1):
        movements.append(Movement(
            type='skate',
            from_pos={'x': rw_entry[i][0], 'y': rw_entry[i][1]},
            to_pos={'x': rw_entry[i+1][0], 'y': rw_entry[i+1][1]},
            style='solid',
            label=''
        ))
    
    # Pass to LW
    movements.append(Movement(type='pass', from_pos={'x': 55, 'y': -8},
                             to_pos={'x': 55, 'y': -28}, style='dotted', label='Pass'))

    spec.movements = movements
    
    builder = DiagramBuilder()
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_part2_phase1_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Part 2 Phase 1 created: {result}')
    return result, spec_path


def create_drill3_part2_phase2(output_path=None):
    """Part 2 Phase 2: Attack Pattern"""
    
    spec = DiagramSpec(
        title='Drill 3 Part 2: 3v2 - Phase 2 (Attack)',
        rink={'view': 'offensive'},
        players=[
            # Positions after entry
            Player(type='forward', position='LW', coordinates={'x': 55, 'y': -28},
                   team='home', has_puck=True, label='LW'),
            Player(type='forward', position='C', coordinates={'x': 55, 'y': -8},
                   team='home', has_puck=False, label='C'),
            Player(type='forward', position='RW', coordinates={'x': 55, 'y': 12},
                   team='home', has_puck=False, label='RW'),
            
            Player(type='defense', position='LD', coordinates={'x': 50, 'y': -15},
                   team='away', has_puck=False, label='D'),
            Player(type='defense', position='RD', coordinates={'x': 50, 'y': 15},
                   team='away', has_puck=False, label='D'),
            
            Player(type='goalie', position='G', coordinates={'x': 83, 'y': 0},
                   team='away', label='G'),
        ],
        movements=[],
        zones=[],
        annotations=[
            Annotation(text='PHASE 2: Attack Pattern', position={'x': 62.5, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='LW goes wide • C drives net • RW stays high • D reacts', position={'x': 62.5, 'y': 35},
                      size='small', style='normal'),
            Annotation(text='Options: A) Shot  B) Pass high  C) Pass net', position={'x': 62.5, 'y': 32},
                      size='small', style='normal'),
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'phase': 2
        }
    )

    movements = []
    
    # LW goes wide with curve
    lw_wide = [
        (55, -28),     # Start
        (62, -32),     # Continue wide
        (70, -35),     # Deep wide
        (75, -32)      # Attack position
    ]
    for i in range(len(lw_wide) - 1):
        label = 'Go wide' if i == 1 else ''
        movements.append(Movement(
            type='carry',
            from_pos={'x': lw_wide[i][0], 'y': lw_wide[i][1]},
            to_pos={'x': lw_wide[i+1][0], 'y': lw_wide[i+1][1]},
            style='solid',
            with_puck=True,
            label=label
        ))
    
    # Centre drives to net with curve
    c_drive = [
        (55, -8),      # Start
        (62, -5),      # Angle toward net
        (70, -3),      # Continue drive
        (77, -2)       # Net front
    ]
    for i in range(len(c_drive) - 1):
        label = 'Drive net' if i == 1 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': c_drive[i][0], 'y': c_drive[i][1]},
            to_pos={'x': c_drive[i+1][0], 'y': c_drive[i+1][1]},
            style='solid',
            label=label
        ))
    
    # RW stays high with slight movement
    movements.append(Movement(type='skate', from_pos={'x': 55, 'y': 12},
                             to_pos={'x': 60, 'y': 10}, style='solid', label='Stay high'))
    
    # Defense reactions
    movements.append(Movement(type='pressure', from_pos={'x': 50, 'y': -15},
                             to_pos={'x': 65, 'y': -28}, style='solid', label='Angle'))
    movements.append(Movement(type='skate', from_pos={'x': 50, 'y': 15},
                             to_pos={'x': 75, 'y': 5}, style='solid', label='Protect'))
    
    # Show options (lighter lines)
    movements.append(Movement(type='shot', from_pos={'x': 75, 'y': -32},
                             to_pos={'x': 83, 'y': 0}, style='dashed', label='A: Shot'))
    movements.append(Movement(type='pass', from_pos={'x': 75, 'y': -32},
                             to_pos={'x': 60, 'y': 10}, style='dotted', label='B: High'))
    movements.append(Movement(type='pass', from_pos={'x': 75, 'y': -32},
                             to_pos={'x': 77, 'y': -2}, style='dotted', label='C: Net'))

    spec.movements = movements
    
    builder = DiagramBuilder()
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_part2_phase2_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Part 2 Phase 2 created: {result}')
    return result, spec_path


def create_all_phases():
    """Create all phase diagrams"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    results = []
    
    # Part 1 - Breakout (3 phases)
    print("\nCreating Part 1: Breakout phases...")
    results.append(create_drill3_part1_phase1(f'../../outputs/drill3_part1_phase1_{timestamp}.png'))
    results.append(create_drill3_part1_phase2(f'../../outputs/drill3_part1_phase2_{timestamp}.png'))
    results.append(create_drill3_part1_phase3(f'../../outputs/drill3_part1_phase3_{timestamp}.png'))
    
    # Part 2 - 3v2 (2 phases)
    print("\nCreating Part 2: 3v2 phases...")
    results.append(create_drill3_part2_phase1(f'../../outputs/drill3_part2_phase1_{timestamp}.png'))
    results.append(create_drill3_part2_phase2(f'../../outputs/drill3_part2_phase2_{timestamp}.png'))
    
    print(f"\nCreated {len(results)} phase diagrams")
    return results


if __name__ == "__main__":
    create_all_phases()