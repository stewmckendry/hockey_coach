#!/usr/bin/env python3
"""
Drill 7: Down Low Give and Go
Two-sided drill with vertical give-and-go alignment for quick passing skills.

Based on approved plan:
- LEFT SIDE: X1 at left circle (-69, 22.5), Y1 below at (-69, 7.5)
- RIGHT SIDE: X2 at right circle (69, -22.5), Y2 below at (69, -7.5)  
- Vertical give-and-go with X high (35), Y low (15)
- Both sides run simultaneously
- Cross-ice rotation after shooting
- Clear labeling of passes and movements
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
sys.path.append('hockey_diagram_mcp/src')

from hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation
from drill_utilities import *

def create_drill_7_down_low_give_and_go():
    """Create the Down Low Give and Go drill diagram."""
    
    # Set up players for both sides with proper vertical alignment
    players = []
    
    # LEFT SIDE - Players in vertical give-and-go formation
    # X1 - High player at left circle (puck carrier)
    players.append(Player(
        type='forward',
        position='X1',
        coordinates={'x': -69, 'y': 22.5},  # Left circle center
        team='home',
        has_puck=True,
        label='X1'
    ))
    
    # Y1 - Low player below left circle
    players.append(Player(
        type='forward', 
        position='Y1',
        coordinates={'x': -69, 'y': 7.5},   # 15 units below X1
        team='home',
        has_puck=False,
        label='Y1'
    ))
    
    # LEFT SIDE - Queue of waiting players
    players.extend(create_player_queue(
        lead_pos={'x': -69, 'y': 35},  # Behind X1
        lead_label='X',
        queue_size=2,
        spacing=5,
        direction='vertical',
        team='home',
        has_puck=False
    ))
    
    # RIGHT SIDE - Players in vertical give-and-go formation  
    # X2 - High player at right circle (puck carrier)
    players.append(Player(
        type='forward',
        position='X2',
        coordinates={'x': 69, 'y': -22.5},  # Right circle center
        team='away',
        has_puck=True,
        label='X2'
    ))
    
    # Y2 - Low player below right circle
    players.append(Player(
        type='forward',
        position='Y2', 
        coordinates={'x': 69, 'y': -7.5},   # 15 units above X2
        team='away',
        has_puck=False,
        label='Y2'
    ))
    
    # RIGHT SIDE - Queue of waiting players
    players.extend(create_player_queue(
        lead_pos={'x': 69, 'y': -35},  # Behind X2
        lead_label='X',
        queue_size=2,
        spacing=5,
        direction='vertical',
        team='away',
        has_puck=False
    ))
    
    # Goalies in both nets
    players.append(Player(
        type='goalie',
        position='G1',
        coordinates={'x': -83, 'y': 0},
        team='home',
        label='G1'
    ))
    
    players.append(Player(
        type='goalie',
        position='G2',
        coordinates={'x': 83, 'y': 0},
        team='away',
        label='G2'
    ))
    
    # Create movements for both sides showing complete give-and-go sequence
    movements = []
    
    # LEFT SIDE MOVEMENTS
    # 1. X1 passes down to Y1
    movements.append(Movement(
        type='pass',
        from_pos={'x': -69, 'y': 22.5},
        to_pos={'x': -69, 'y': 7.5},
        style='dotted',
        label='Pass Down'
    ))
    
    # 2. X1 drives to net (high route to slot)
    movements.append(Movement(
        type='skate',
        from_pos={'x': -69, 'y': 22.5},
        to_pos={'x': -75, 'y': 10},  # Slot position for shot
        style='solid',
        label='Drive High'
    ))
    
    # 3. Y1 returns pass up to X1
    movements.append(Movement(
        type='pass',
        from_pos={'x': -69, 'y': 7.5},
        to_pos={'x': -75, 'y': 10},
        style='dotted',
        label='Return Pass'
    ))
    
    # 4. X1 shoots from slot
    movements.append(Movement(
        type='shot',
        from_pos={'x': -75, 'y': 10},
        to_pos={'x': -83, 'y': 0},
        style='dashed',
        label='Shot'
    ))
    
    # 5. Y1 rotates cross-ice to join right side queue
    movements.append(Movement(
        type='skate',
        from_pos={'x': -69, 'y': 7.5},
        to_pos={'x': 69, 'y': -40},  # Cross-ice to right queue
        style='solid',
        label='Rotate'
    ))
    
    # RIGHT SIDE MOVEMENTS (mirror of left side)
    # 1. X2 passes down to Y2
    movements.append(Movement(
        type='pass',
        from_pos={'x': 69, 'y': -22.5},
        to_pos={'x': 69, 'y': -7.5},
        style='dotted',
        label='Pass Down'
    ))
    
    # 2. X2 drives to net (high route to slot)
    movements.append(Movement(
        type='skate',
        from_pos={'x': 69, 'y': -22.5},
        to_pos={'x': 75, 'y': -10},  # Slot position for shot
        style='solid', 
        label='Drive High'
    ))
    
    # 3. Y2 returns pass up to X2
    movements.append(Movement(
        type='pass',
        from_pos={'x': 69, 'y': -7.5},
        to_pos={'x': 75, 'y': -10},
        style='dotted',
        label='Return Pass'
    ))
    
    # 4. X2 shoots from slot
    movements.append(Movement(
        type='shot',
        from_pos={'x': 75, 'y': -10},
        to_pos={'x': 83, 'y': 0},
        style='dashed',
        label='Shot'
    ))
    
    # 5. Y2 rotates cross-ice to join left side queue
    movements.append(Movement(
        type='skate',
        from_pos={'x': 69, 'y': -7.5},
        to_pos={'x': -69, 'y': 40},  # Cross-ice to left queue
        style='solid',
        label='Rotate'
    ))
    
    # Add zones for visual clarity (no equipment needed for this drill)
    zones = []
    
    # Left side give-and-go zone
    zones.append(Zone(
        type='coverage',
        shape='rectangle',
        bounds={'x': -74, 'y': 5, 'width': 10, 'height': 20},
        team='home',
        opacity=0.1,
        color='blue',
        label=''
    ))
    
    # Right side give-and-go zone
    zones.append(Zone(
        type='coverage',
        shape='rectangle', 
        bounds={'x': 64, 'y': -25, 'width': 10, 'height': 20},
        team='away',
        opacity=0.1,
        color='red',
        label=''
    ))
    
    # Create annotations
    annotations = create_standard_annotations([
        'Both sides run simultaneously',
        'Vertical give-and-go alignment - high player to low player',
        'Quick pass and drive to create scoring opportunity',
        'Cross-ice rotation maintains continuous flow',
        'Focus on timing and communication between partners'
    ], y_start=-35)
    
    # Build the complete specification
    spec = DiagramSpec(
        title='Drill 7: Down Low Give and Go',
        rink={'view': 'full'},  # Full rink view to show both sides and rotation
        players=players,
        movements=movements, 
        zones=zones,
        annotations=annotations,
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'passing_drill',
            'skill_focus': 'give_and_go',
            'player_count': '4+',
            'ice_time': '10-15_minutes'
        }
    )
    
    # Validate before building
    issues = validate_diagram_elements(spec)
    if issues:
        print("Validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
    
    # Build and save the diagram
    builder = DiagramBuilder()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'/Users/liammckendry/hockey_coach_issue-111/hockey_diagram_mcp/outputs/drill_7_down_low_give_and_go.png'
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Build the diagram
    builder.build(spec, output_path)
    
    # Save the specification for reference
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        json.dump(asdict(spec), f, indent=2)
    
    print(f"Drill 7 diagram saved to: {output_path}")
    print(f"Specification saved to: {spec_path}")
    
    return output_path, spec_path

if __name__ == "__main__":
    # Activate virtual environment and run
    import os
    print("Creating Drill 7: Down Low Give and Go diagram...")
    
    try:
        create_drill_7_down_low_give_and_go()
        print("✓ Diagram created successfully!")
    except Exception as e:
        print(f"Error creating diagram: {e}")
        import traceback
        traceback.print_exc()