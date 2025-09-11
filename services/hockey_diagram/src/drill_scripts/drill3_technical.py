#!/usr/bin/env python
"""
Drill 3: 3v2 Breakout & Forecheck - TECHNICALLY ACCURATE VERSION
Iteration 4: Correct technical implementation with proper positioning and movements
Created: 2025-08-27

Three distinct phases with accurate hockey systems play.
"""

import sys
import numpy as np
from datetime import datetime
from pathlib import Path
sys.path.append('..')

from hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation
from drill_utilities import generate_arc_points, STANDARD_POSITIONS, Z_ORDER


def create_phase1_dumpin(output_path=None):
    """Phase 1: Dump-in from Neutral Zone"""
    
    spec = DiagramSpec(
        title='Drill 3 - Phase 1: Dump-in & Positioning',
        rink={'view': 'full'},  # Need to see neutral zone and defensive zone
        players=[
            # Starting positions in NEUTRAL ZONE
            # Defense on blue line
            Player(type='defense', position='LD', coordinates={'x': -25, 'y': -15},
                   team='home', has_puck=False, label='LD'),
            Player(type='defense', position='RD', coordinates={'x': -25, 'y': 15},
                   team='home', has_puck=False, label='RD'),
            
            # Forwards on red line
            Player(type='forward', position='RW', coordinates={'x': 0, 'y': -22.5},
                   team='home', has_puck=False, label='RW'),
            Player(type='forward', position='C', coordinates={'x': 0, 'y': 0},
                   team='home', has_puck=False, label='C'),
            Player(type='forward', position='LW', coordinates={'x': 0, 'y': 22.5},
                   team='home', has_puck=False, label='LW'),
            
            # Coach with puck
            Player(type='coach', position='Coach', coordinates={'x': 10, 'y': 0},
                   team='neutral', has_puck=True, label='C'),
            
            # Goalie
            Player(type='goalie', position='G', coordinates={'x': -83, 'y': 0},
                   team='home', label='G'),
                   
            # Puck destination in corner
            Player(type='puck', position='Puck', coordinates={'x': -85, 'y': 35},
                   team='neutral', has_puck=False),
        ],
        movements=[],
        zones=[],
        annotations=[
            Annotation(text='PHASE 1: Dump-in & Positioning', position={'x': 0, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='Movement Keys:', position={'x': -50, 'y': -32},
                      size='medium', style='bold'),
            Annotation(text='• Closest D (RD) → puck', position={'x': -50, 'y': -34.5},
                      size='small', style='normal'),
            Annotation(text='• Other D (LD) → net front', position={'x': -50, 'y': -36.5},
                      size='small', style='normal'),
            Annotation(text='• Closest F (LW) → hashmark boards', position={'x': -50, 'y': -38.5},
                      size='small', style='normal'),
            Annotation(text='• C → support (curl around dot)', position={'x': -50, 'y': -40.5},
                      size='small', style='normal'),
            Annotation(text='• Far F (RW) → middle ice', position={'x': -50, 'y': -42.5},
                      size='small', style='normal'),
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'phase': 1
        }
    )

    movements = []
    
    # 1. Coach dumps puck into corner
    movements.append(Movement(type='pass', from_pos={'x': 10, 'y': 0},
                             to_pos={'x': -85, 'y': 35}, style='dotted', label='Dump'))
    
    # 2. RD (closest D) goes to puck with short curl back
    rd_path = [
        (-25, 15),     # Start
        (-45, 20),     # Move toward corner
        (-65, 28),     # Continue
        (-80, 33),     # Near puck
        (-82, 30),     # Short curl back
        (-78, 28)      # Final position
    ]
    for i in range(len(rd_path) - 1):
        label = 'To puck' if i == 2 else 'Curl' if i == 4 else ''
        style = 'dashed' if i >= 3 else 'solid'
        movements.append(Movement(
            type='skate',
            from_pos={'x': rd_path[i][0], 'y': rd_path[i][1]},
            to_pos={'x': rd_path[i+1][0], 'y': rd_path[i+1][1]},
            style=style,
            label=label
        ))
    
    # 3. LD (other D) goes to net front with short curl
    ld_path = [
        (-25, -15),    # Start
        (-45, -10),    # Move toward net
        (-65, -5),     # Continue
        (-78, 2),      # Net front
        (-80, 5),      # Short curl
        (-78, 5)       # Final position
    ]
    for i in range(len(ld_path) - 1):
        label = 'Net front' if i == 2 else ''
        style = 'dashed' if i >= 3 else 'solid'
        movements.append(Movement(
            type='skate',
            from_pos={'x': ld_path[i][0], 'y': ld_path[i][1]},
            to_pos={'x': ld_path[i+1][0], 'y': ld_path[i+1][1]},
            style=style,
            label=label
        ))
    
    # 4. LW (closest F) goes to hashmark boards with curl
    lw_path = [
        (0, 22.5),     # Start
        (-25, 28),     # Enter zone
        (-50, 35),     # Move to boards
        (-69, 38),     # Hashmark boards
        (-72, 35),     # Short curl back
        (-69, 36)      # Final position
    ]
    for i in range(len(lw_path) - 1):
        label = 'Hashmarks' if i == 2 else ''
        style = 'dashed' if i >= 3 else 'solid'
        movements.append(Movement(
            type='skate',
            from_pos={'x': lw_path[i][0], 'y': lw_path[i][1]},
            to_pos={'x': lw_path[i+1][0], 'y': lw_path[i+1][1]},
            style=style,
            label=label
        ))
    
    # 5. Centre goes to support - curl around upper dot
    c_path = [
        (0, 0),        # Start
        (-25, 8),      # Enter zone
        (-50, 15),     # Approach dot
        (-65, 20),     # Around dot
        (-69, 22.5),   # Faceoff dot
        (-72, 20),     # Curl around
        (-70, 18),     # Complete curl
        (-65, 20)      # Support position
    ]
    for i in range(len(c_path) - 1):
        label = 'Support' if i == 2 else 'Curl' if i == 5 else ''
        style = 'dashed' if i >= 4 else 'solid'
        movements.append(Movement(
            type='skate',
            from_pos={'x': c_path[i][0], 'y': c_path[i][1]},
            to_pos={'x': c_path[i+1][0], 'y': c_path[i+1][1]},
            style=style,
            label=label
        ))
    
    # 6. RW (far winger) goes to middle ice with curl
    rw_path = [
        (0, -22.5),    # Start
        (-25, -15),    # Enter zone
        (-45, -5),     # Move to middle
        (-50, 0),      # Middle ice
        (-52, 3),      # Short curl
        (-50, 2)       # Final position
    ]
    for i in range(len(rw_path) - 1):
        label = 'Middle' if i == 2 else ''
        style = 'dashed' if i >= 3 else 'solid'
        movements.append(Movement(
            type='skate',
            from_pos={'x': rw_path[i][0], 'y': rw_path[i][1]},
            to_pos={'x': rw_path[i+1][0], 'y': rw_path[i+1][1]},
            style=style,
            label=label
        ))

    spec.movements = movements
    
    builder = DiagramBuilder()
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_phase1_dumpin_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Phase 1 created: {result}')
    return result, spec_path


def create_phase2_breakout(output_path=None):
    """Phase 2: Breakout from Defensive Zone"""
    
    spec = DiagramSpec(
        title='Drill 3 - Phase 2: Breakout Passing',
        rink={'view': 'full'},  # Need to see exit to neutral zone
        players=[
            # Positions after Phase 1
            Player(type='defense', position='RD', coordinates={'x': -78, 'y': 28},
                   team='home', has_puck=True, label='RD'),
            Player(type='defense', position='LD', coordinates={'x': -78, 'y': 5},
                   team='home', has_puck=False, label='LD'),
            
            Player(type='forward', position='LW', coordinates={'x': -69, 'y': 36},
                   team='home', has_puck=False, label='LW'),
            Player(type='forward', position='C', coordinates={'x': -65, 'y': 20},
                   team='home', has_puck=False, label='C'),
            Player(type='forward', position='RW', coordinates={'x': -50, 'y': 2},
                   team='home', has_puck=False, label='RW'),
            
            # Coach at far blue line
            Player(type='coach', position='Coach', coordinates={'x': 25, 'y': 0},
                   team='neutral', has_puck=False, label='C'),
            
            Player(type='goalie', position='G', coordinates={'x': -83, 'y': 0},
                   team='home', label='G'),
        ],
        movements=[],
        zones=[],
        annotations=[
            Annotation(text='PHASE 2: Breakout Passing Sequence', position={'x': 0, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='Pass Sequence:', position={'x': -50, 'y': -32},
                      size='medium', style='bold'),
            Annotation(text='1. D → Winger on boards', position={'x': -50, 'y': -34.5},
                      size='small', style='normal'),
            Annotation(text='2. Winger → Centre (moving up)', position={'x': -50, 'y': -36.5},
                      size='small', style='normal'),
            Annotation(text='3. Centre → Other winger (far up)', position={'x': -50, 'y': -38.5},
                      size='small', style='normal'),
            Annotation(text='4. Winger → Coach', position={'x': -50, 'y': -40.5},
                      size='small', style='normal'),
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'phase': 2
        }
    )

    movements = []
    
    # Pass 1: RD to LW on boards
    movements.append(Movement(type='pass', from_pos={'x': -78, 'y': 28},
                             to_pos={'x': -69, 'y': 36}, style='dotted', label='1'))
    
    # LW starts moving up ice
    lw_move = [
        (-69, 36),     # Start
        (-55, 32),     # Move up
        (-40, 28),     # Continue
        (-25, 25)      # Blue line area
    ]
    for i in range(len(lw_move) - 1):
        movements.append(Movement(
            type='carry' if i == 0 else 'skate',
            from_pos={'x': lw_move[i][0], 'y': lw_move[i][1]},
            to_pos={'x': lw_move[i+1][0], 'y': lw_move[i+1][1]},
            style='solid',
            with_puck=(i == 0),
            label=''
        ))
    
    # Centre moves up ice to receive pass
    c_move = [
        (-65, 20),     # Start
        (-45, 15),     # Move up
        (-25, 10),     # Blue line
        (-10, 8)       # Neutral zone
    ]
    for i in range(len(c_move) - 1):
        movements.append(Movement(
            type='skate',
            from_pos={'x': c_move[i][0], 'y': c_move[i][1]},
            to_pos={'x': c_move[i+1][0], 'y': c_move[i+1][1]},
            style='solid',
            label='Moving up' if i == 1 else ''
        ))
    
    # Pass 2: LW to Centre
    movements.append(Movement(type='pass', from_pos={'x': -25, 'y': 25},
                             to_pos={'x': -10, 'y': 8}, style='dotted', label='2'))
    
    # Centre continues with puck
    movements.append(Movement(type='carry', from_pos={'x': -10, 'y': 8},
                             to_pos={'x': 5, 'y': 5}, style='solid', with_puck=True, label=''))
    
    # RW moves up ice and crosses toward middle
    rw_move = [
        (-50, 2),      # Start
        (-30, -5),     # Move up
        (-10, -8),     # Blue line
        (10, -5),      # Neutral zone
        (20, 0)        # Cross to middle
    ]
    for i in range(len(rw_move) - 1):
        movements.append(Movement(
            type='skate',
            from_pos={'x': rw_move[i][0], 'y': rw_move[i][1]},
            to_pos={'x': rw_move[i+1][0], 'y': rw_move[i+1][1]},
            style='solid',
            label='Cross middle' if i == 3 else ''
        ))
    
    # Pass 3: Centre to RW
    movements.append(Movement(type='pass', from_pos={'x': 5, 'y': 5},
                             to_pos={'x': 20, 'y': 0}, style='dotted', label='3'))
    
    # Pass 4: RW to Coach
    movements.append(Movement(type='pass', from_pos={'x': 20, 'y': 0},
                             to_pos={'x': 25, 'y': 0}, style='dotted', label='4'))

    spec.movements = movements
    
    builder = DiagramBuilder()
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_phase2_breakout_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Phase 2 created: {result}')
    return result, spec_path


def create_phase3_forecheck(output_path=None):
    """Phase 3: Forecheck 3v2"""
    
    spec = DiagramSpec(
        title='Drill 3 - Phase 3: Forecheck 3v2',
        rink={'view': 'offensive'},  # Focus on offensive zone
        players=[
            # Starting positions after getting puck back from coach
            Player(type='forward', position='F1', coordinates={'x': 25, 'y': 0},
                   team='home', has_puck=False, label='F1'),
            Player(type='forward', position='F2', coordinates={'x': 25, 'y': 15},
                   team='home', has_puck=False, label='F2'),
            Player(type='forward', position='F3', coordinates={'x': 25, 'y': -15},
                   team='home', has_puck=False, label='F3'),
            
            # Defense in position
            Player(type='defense', position='D1', coordinates={'x': 50, 'y': -15},
                   team='away', has_puck=False, label='D1'),
            Player(type='defense', position='D2', coordinates={'x': 50, 'y': 15},
                   team='away', has_puck=False, label='D2'),
            
            # Coach dumps puck
            Player(type='coach', position='Coach', coordinates={'x': 25, 'y': 30},
                   team='neutral', has_puck=True, label='C'),
            
            # Goalie
            Player(type='goalie', position='G', coordinates={'x': 83, 'y': 0},
                   team='away', label='G'),
                   
            # Puck in corner
            Player(type='puck', position='Puck', coordinates={'x': 85, 'y': 35},
                   team='neutral', has_puck=False),
        ],
        movements=[],
        zones=[],
        annotations=[
            Annotation(text='PHASE 3: Forecheck 3v2', position={'x': 62.5, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='Roles:', position={'x': 45, 'y': -32},
                      size='medium', style='bold'),
            Annotation(text='F1: "Batman" - Pressure puck carrier', position={'x': 45, 'y': -34.5},
                      size='small', style='normal'),
            Annotation(text='F2: "Robin" - Support F1 (2-on-1)', position={'x': 45, 'y': -36.5},
                      size='small', style='normal'),
            Annotation(text='F3: "Spider-Man" - Stay high', position={'x': 45, 'y': -38.5},
                      size='small', style='normal'),
            Annotation(text='D1: Closest D gets puck', position={'x': 45, 'y': -40.5},
                      size='small', style='normal'),
            Annotation(text='D2: Other D protects net', position={'x': 45, 'y': -42.5},
                      size='small', style='normal'),
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'phase': 3
        }
    )

    movements = []
    
    # Coach dumps puck into corner
    movements.append(Movement(type='pass', from_pos={'x': 25, 'y': 30},
                             to_pos={'x': 85, 'y': 35}, style='dotted', label='Dump'))
    
    # D2 (closest) goes to puck
    d2_path = [
        (50, 15),      # Start
        (60, 20),      # Move toward corner
        (70, 28),      # Continue
        (82, 33)       # Get puck
    ]
    for i in range(len(d2_path) - 1):
        label = 'Get puck' if i == 2 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': d2_path[i][0], 'y': d2_path[i][1]},
            to_pos={'x': d2_path[i+1][0], 'y': d2_path[i+1][1]},
            style='solid',
            label=label
        ))
    
    # D1 goes to net front
    d1_path = [
        (50, -15),     # Start
        (65, -8),      # Move to net
        (75, -2),      # Net front area
        (78, 3)        # Protect net
    ]
    for i in range(len(d1_path) - 1):
        label = 'Net front' if i == 2 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': d1_path[i][0], 'y': d1_path[i][1]},
            to_pos={'x': d1_path[i+1][0], 'y': d1_path[i+1][1]},
            style='solid',
            label=label
        ))
    
    # F1 (Batman) - pressure D with puck
    f1_path = [
        (25, 0),       # Start
        (45, 10),      # Angle toward D
        (65, 20),      # Continue pressure
        (78, 30)       # Pressure point
    ]
    for i in range(len(f1_path) - 1):
        label = 'Batman' if i == 1 else 'Pressure' if i == 2 else ''
        movements.append(Movement(
            type='pressure' if i == 2 else 'skate',
            from_pos={'x': f1_path[i][0], 'y': f1_path[i][1]},
            to_pos={'x': f1_path[i+1][0], 'y': f1_path[i+1][1]},
            style='solid',
            label=label
        ))
    
    # F2 (Robin) - support F1 to create 2-on-1
    f2_path = [
        (25, 15),      # Start
        (45, 20),      # Move to support
        (60, 25),      # Position for 2-on-1
        (70, 22)       # Support position
    ]
    for i in range(len(f2_path) - 1):
        label = 'Robin' if i == 1 else '2-on-1' if i == 2 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': f2_path[i][0], 'y': f2_path[i][1]},
            to_pos={'x': f2_path[i+1][0], 'y': f2_path[i+1][1]},
            style='solid',
            label=label
        ))
    
    # F3 (Spider-Man) - stay high for support
    f3_path = [
        (25, -15),     # Start
        (45, -10),     # Move to high slot
        (55, -5),      # High support position
        (60, 0)        # Middle ice
    ]
    for i in range(len(f3_path) - 1):
        label = 'Spider-Man' if i == 1 else 'High support' if i == 2 else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': f3_path[i][0], 'y': f3_path[i][1]},
            to_pos={'x': f3_path[i+1][0], 'y': f3_path[i+1][1]},
            style='dashed' if i >= 2 else 'solid',
            label=label
        ))
    
    # Show potential pass option from D
    movements.append(Movement(type='pass', from_pos={'x': 82, 'y': 33},
                             to_pos={'x': 78, 'y': 3}, style='dotted', label='Option'))

    spec.movements = movements
    
    builder = DiagramBuilder()
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_phase3_forecheck_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Phase 3 created: {result}')
    return result, spec_path


def create_all_technical_phases():
    """Create all technically accurate phase diagrams"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    results = []
    
    print("\nCreating Technically Accurate Drill 3 Phases...")
    print("-" * 50)
    
    # Phase 1: Dump-in
    print("Creating Phase 1: Dump-in & Positioning...")
    results.append(create_phase1_dumpin(f'../../outputs/drill3_phase1_dumpin_{timestamp}.png'))
    
    # Phase 2: Breakout
    print("Creating Phase 2: Breakout Passing...")
    results.append(create_phase2_breakout(f'../../outputs/drill3_phase2_breakout_{timestamp}.png'))
    
    # Phase 3: Forecheck
    print("Creating Phase 3: Forecheck 3v2...")
    results.append(create_phase3_forecheck(f'../../outputs/drill3_phase3_forecheck_{timestamp}.png'))
    
    print(f"\n✓ Created {len(results)} technically accurate phase diagrams")
    print(f"✓ Timestamp: {timestamp}")
    return results


if __name__ == "__main__":
    create_all_technical_phases()