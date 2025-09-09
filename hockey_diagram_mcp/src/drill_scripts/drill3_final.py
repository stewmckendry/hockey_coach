#!/usr/bin/env python
"""
Drill 3: FINAL VERSION with Smooth Waypoint Movements
All three phases with natural curved skating paths
Created: 2025-08-27 (Final)

Uses the new waypoints feature in DiagramBuilder for smooth movements.
"""

import sys
from datetime import datetime
sys.path.append('..')

from hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation


def create_phase1_final(output_path=None):
    """Phase 1: Dump-in & Positioning with smooth movements"""
    
    spec = DiagramSpec(
        title='Drill 3 - Phase 1: Dump-in & Positioning',
        rink={'view': 'full'},
        players=[
            # Starting positions in NEUTRAL ZONE
            Player(type='defense', position='LD', coordinates={'x': -25, 'y': -15},
                   team='home', has_puck=False, label='LD'),
            Player(type='defense', position='RD', coordinates={'x': -25, 'y': 15},
                   team='home', has_puck=False, label='RD'),
            
            Player(type='forward', position='RW', coordinates={'x': 0, 'y': -22.5},
                   team='home', has_puck=False, label='RW'),
            Player(type='forward', position='C', coordinates={'x': 0, 'y': 0},
                   team='home', has_puck=False, label='C'),
            Player(type='forward', position='LW', coordinates={'x': 0, 'y': 22.5},
                   team='home', has_puck=False, label='LW'),
            
            Player(type='coach', position='Coach', coordinates={'x': 10, 'y': 0},
                   team='neutral', has_puck=True, label='C'),
            
            Player(type='goalie', position='G', coordinates={'x': -83, 'y': 0},
                   team='home', label='G'),
                   
            # Puck destination in corner
            Player(type='puck', position='Puck', coordinates={'x': -85, 'y': 35},
                   team='neutral', has_puck=False),
        ],
        movements=[
            # Coach dumps puck (straight pass is fine)
            Movement(type='pass', from_pos={'x': 10, 'y': 0},
                    to_pos={'x': -85, 'y': 35}, style='dotted', label='Dump'),
            
            # RD to puck with smooth curve and curl back
            Movement(
                type='skate',
                from_pos={'x': -25, 'y': 15},
                to_pos={'x': -78, 'y': 28},
                label='To puck',
                waypoints=[
                    (-25, 15),     # Start
                    (-45, 20),     # Control point
                    (-65, 28),     # Approach puck
                    (-80, 33),     # Get puck
                    (-82, 30),     # Curl back
                    (-78, 28)      # Final position
                ]
            ),
            
            # LD to net front with smooth curve
            Movement(
                type='skate',
                from_pos={'x': -25, 'y': -15},
                to_pos={'x': -78, 'y': 5},
                label='Net front',
                waypoints=[
                    (-25, -15),    # Start
                    (-45, -10),    # Control
                    (-65, -5),     # Approach
                    (-78, 2),      # Net position
                    (-80, 5),      # Small curl
                    (-78, 5)       # Final
                ]
            ),
            
            # LW to hashmarks with smooth curve
            Movement(
                type='skate',
                from_pos={'x': 0, 'y': 22.5},
                to_pos={'x': -69, 'y': 36},
                label='Hashmarks',
                waypoints=[
                    (0, 22.5),     # Start
                    (-25, 28),     # Enter zone
                    (-50, 35),     # Continue
                    (-69, 38),     # Hashmarks
                    (-72, 35),     # Curl back
                    (-69, 36)      # Final
                ]
            ),
            
            # Centre support with curl around dot
            Movement(
                type='skate',
                from_pos={'x': 0, 'y': 0},
                to_pos={'x': -65, 'y': 20},
                label='Support',
                style='dashed',
                waypoints=[
                    (0, 0),        # Start
                    (-25, 8),      # Enter zone
                    (-50, 15),     # Approach dot
                    (-65, 20),     # Near dot
                    (-69, 22.5),   # At dot
                    (-72, 20),     # Curl around
                    (-70, 18),     # Continue curl
                    (-65, 20)      # Support position
                ]
            ),
            
            # RW to middle ice with smooth curve
            Movement(
                type='skate',
                from_pos={'x': 0, 'y': -22.5},
                to_pos={'x': -50, 'y': 2},
                label='Middle',
                style='dashed',
                waypoints=[
                    (0, -22.5),    # Start
                    (-25, -15),    # Enter zone
                    (-45, -5),     # Curve to middle
                    (-50, 0),      # Middle ice
                    (-52, 3),      # Small curl
                    (-50, 2)       # Final
                ]
            ),
        ],
        zones=[],
        annotations=[
            Annotation(text='PHASE 1: Dump-in & Positioning', position={'x': 0, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='Movement Keys:', position={'x': -50, 'y': -32},
                      size='medium', style='bold'),
            Annotation(text='• RD retrieves puck with curl', position={'x': -50, 'y': -34.5},
                      size='small', style='normal'),
            Annotation(text='• LD protects net front', position={'x': -50, 'y': -36.5},
                      size='small', style='normal'),
            Annotation(text='• LW supports at hashmarks', position={'x': -50, 'y': -38.5},
                      size='small', style='normal'),
            Annotation(text='• C curls for support', position={'x': -50, 'y': -40.5},
                      size='small', style='normal'),
            Annotation(text='• RW covers middle ice', position={'x': -50, 'y': -42.5},
                      size='small', style='normal'),
        ],
        metadata={'created': datetime.now().isoformat(), 'phase': 1}
    )
    
    builder = DiagramBuilder()
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_phase1_final_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Phase 1 FINAL created: {result}')
    return result, spec_path


def create_phase2_final(output_path=None):
    """Phase 2: Breakout Passing with smooth movements"""
    
    spec = DiagramSpec(
        title='Drill 3 - Phase 2: Breakout Passing',
        rink={'view': 'full'},
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
            
            Player(type='coach', position='Coach', coordinates={'x': 25, 'y': 0},
                   team='neutral', has_puck=False, label='C'),
            
            Player(type='goalie', position='G', coordinates={'x': -83, 'y': 0},
                   team='home', label='G'),
        ],
        movements=[
            # Pass 1: RD to LW (straight pass)
            Movement(type='pass', from_pos={'x': -78, 'y': 28},
                    to_pos={'x': -69, 'y': 36}, style='dotted', label='1'),
            
            # LW moves up ice with puck
            Movement(
                type='carry',
                from_pos={'x': -69, 'y': 36},
                to_pos={'x': -25, 'y': 25},
                with_puck=True,
                label='',
                waypoints=[
                    (-69, 36),     # Start with puck
                    (-55, 32),     # Move up
                    (-40, 28),     # Continue
                    (-25, 25)      # Blue line
                ]
            ),
            
            # Centre moves up to receive pass
            Movement(
                type='skate',
                from_pos={'x': -65, 'y': 20},
                to_pos={'x': -10, 'y': 8},
                label='Moving up',
                waypoints=[
                    (-65, 20),     # Start
                    (-45, 15),     # Move up
                    (-25, 10),     # Blue line
                    (-10, 8)       # Neutral zone
                ]
            ),
            
            # Pass 2: LW to Centre
            Movement(type='pass', from_pos={'x': -25, 'y': 25},
                    to_pos={'x': -10, 'y': 8}, style='dotted', label='2'),
            
            # Centre carries puck
            Movement(
                type='carry',
                from_pos={'x': -10, 'y': 8},
                to_pos={'x': 5, 'y': 5},
                with_puck=True,
                label='',
                waypoints=[
                    (-10, 8),      # Start with puck
                    (0, 7),        # Continue
                    (5, 5)         # Center ice
                ]
            ),
            
            # RW moves up and crosses to middle
            Movement(
                type='skate',
                from_pos={'x': -50, 'y': 2},
                to_pos={'x': 20, 'y': 0},
                label='Cross middle',
                waypoints=[
                    (-50, 2),      # Start
                    (-30, -5),     # Move up
                    (-10, -8),     # Blue line
                    (10, -5),      # Neutral zone
                    (20, 0)        # Cross to middle
                ]
            ),
            
            # Pass 3: Centre to RW
            Movement(type='pass', from_pos={'x': 5, 'y': 5},
                    to_pos={'x': 20, 'y': 0}, style='dotted', label='3'),
            
            # Pass 4: RW to Coach
            Movement(type='pass', from_pos={'x': 20, 'y': 0},
                    to_pos={'x': 25, 'y': 0}, style='dotted', label='4'),
            
            # LW continues up ice
            Movement(
                type='skate',
                from_pos={'x': -25, 'y': 25},
                to_pos={'x': 0, 'y': 20},
                label='',
                style='dashed',
                waypoints=[
                    (-25, 25),     # After pass
                    (-10, 22),     # Continue
                    (0, 20)        # Support position
                ]
            ),
        ],
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
            Annotation(text='3. Centre → Winger (crossing)', position={'x': -50, 'y': -38.5},
                      size='small', style='normal'),
            Annotation(text='4. Winger → Coach', position={'x': -50, 'y': -40.5},
                      size='small', style='normal'),
        ],
        metadata={'created': datetime.now().isoformat(), 'phase': 2}
    )
    
    builder = DiagramBuilder()
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_phase2_final_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Phase 2 FINAL created: {result}')
    return result, spec_path


def create_phase3_final(output_path=None):
    """Phase 3: Forecheck 3v2 with smooth movements"""
    
    spec = DiagramSpec(
        title='Drill 3 - Phase 3: Forecheck 3v2',
        rink={'view': 'offensive'},
        players=[
            # Starting positions
            Player(type='forward', position='F1', coordinates={'x': 25, 'y': 0},
                   team='home', has_puck=False, label='F1'),
            Player(type='forward', position='F2', coordinates={'x': 25, 'y': 15},
                   team='home', has_puck=False, label='F2'),
            Player(type='forward', position='F3', coordinates={'x': 25, 'y': -15},
                   team='home', has_puck=False, label='F3'),
            
            Player(type='defense', position='D1', coordinates={'x': 50, 'y': -15},
                   team='away', has_puck=False, label='D1'),
            Player(type='defense', position='D2', coordinates={'x': 50, 'y': 15},
                   team='away', has_puck=False, label='D2'),
            
            Player(type='coach', position='Coach', coordinates={'x': 25, 'y': 30},
                   team='neutral', has_puck=True, label='C'),
            
            Player(type='goalie', position='G', coordinates={'x': 83, 'y': 0},
                   team='away', label='G'),
                   
            # Puck in corner
            Player(type='puck', position='Puck', coordinates={'x': 85, 'y': 35},
                   team='neutral', has_puck=False),
        ],
        movements=[
            # Coach dumps puck
            Movement(type='pass', from_pos={'x': 25, 'y': 30},
                    to_pos={'x': 85, 'y': 35}, style='dotted', label='Dump'),
            
            # D2 to puck with smooth curve
            Movement(
                type='skate',
                from_pos={'x': 50, 'y': 15},
                to_pos={'x': 82, 'y': 33},
                label='Get puck',
                waypoints=[
                    (50, 15),      # Start
                    (60, 20),      # Move toward corner
                    (70, 28),      # Continue
                    (82, 33)       # Get puck
                ]
            ),
            
            # D1 to net front with smooth curve
            Movement(
                type='skate',
                from_pos={'x': 50, 'y': -15},
                to_pos={'x': 78, 'y': 3},
                label='Net front',
                waypoints=[
                    (50, -15),     # Start
                    (65, -8),      # Move to net
                    (75, -2),      # Approach net
                    (78, 3)        # Protect net
                ]
            ),
            
            # F1 (Batman) pressures D with puck
            Movement(
                type='pressure',
                from_pos={'x': 25, 'y': 0},
                to_pos={'x': 78, 'y': 30},
                label='Batman',
                waypoints=[
                    (25, 0),       # Start
                    (45, 10),      # Angle toward D
                    (65, 20),      # Continue pressure
                    (78, 30)       # Pressure point
                ]
            ),
            
            # F2 (Robin) supports for 2-on-1
            Movement(
                type='skate',
                from_pos={'x': 25, 'y': 15},
                to_pos={'x': 70, 'y': 22},
                label='Robin',
                waypoints=[
                    (25, 15),      # Start
                    (45, 20),      # Move to support
                    (60, 25),      # Position for 2-on-1
                    (70, 22)       # Support position
                ]
            ),
            
            # F3 (Spider-Man) stays high
            Movement(
                type='skate',
                from_pos={'x': 25, 'y': -15},
                to_pos={'x': 60, 'y': 0},
                label='Spider-Man',
                style='dashed',
                waypoints=[
                    (25, -15),     # Start
                    (45, -10),     # Move to high slot
                    (55, -5),      # Continue
                    (60, 0)        # Middle ice support
                ]
            ),
            
            # Potential pass option
            Movement(type='pass', from_pos={'x': 82, 'y': 33},
                    to_pos={'x': 78, 'y': 3}, style='dotted', label='Option'),
        ],
        zones=[],
        annotations=[
            Annotation(text='PHASE 3: Forecheck 3v2', position={'x': 62.5, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='Roles:', position={'x': 45, 'y': -32},
                      size='medium', style='bold'),
            Annotation(text='F1: "Batman" - Pressure puck', position={'x': 45, 'y': -34.5},
                      size='small', style='normal'),
            Annotation(text='F2: "Robin" - Support (2-on-1)', position={'x': 45, 'y': -36.5},
                      size='small', style='normal'),
            Annotation(text='F3: "Spider-Man" - High support', position={'x': 45, 'y': -38.5},
                      size='small', style='normal'),
            Annotation(text='D1: Closest gets puck', position={'x': 45, 'y': -40.5},
                      size='small', style='normal'),
            Annotation(text='D2: Other protects net', position={'x': 45, 'y': -42.5},
                      size='small', style='normal'),
        ],
        metadata={'created': datetime.now().isoformat(), 'phase': 3}
    )
    
    builder = DiagramBuilder()
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_phase3_final_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Phase 3 FINAL created: {result}')
    return result, spec_path


def create_all_phases_final():
    """Create all three phases with smooth movements"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("\n" + "="*60)
    print("Creating FINAL Drill 3 with Smooth Waypoint Movements")
    print("="*60)
    
    results = []
    
    # Phase 1
    print("\n📍 Creating Phase 1: Dump-in & Positioning...")
    results.append(create_phase1_final(f'../../outputs/drill3_phase1_final_{timestamp}.png'))
    
    # Phase 2
    print("📍 Creating Phase 2: Breakout Passing...")
    results.append(create_phase2_final(f'../../outputs/drill3_phase2_final_{timestamp}.png'))
    
    # Phase 3
    print("📍 Creating Phase 3: Forecheck 3v2...")
    results.append(create_phase3_final(f'../../outputs/drill3_phase3_final_{timestamp}.png'))
    
    print("\n" + "="*60)
    print(f"✅ Successfully created {len(results)} phase diagrams")
    print(f"✅ All movements use smooth curved paths")
    print(f"✅ Timestamp: {timestamp}")
    print("="*60)
    
    return results


if __name__ == "__main__":
    create_all_phases_final()