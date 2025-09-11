#!/usr/bin/env python3
"""
U11 - SKATING - WARM UP
Basic skating warm-up drill with two lines at hashmarks.
Players skate down middle of ice to far end, return along boards.

Based on approved plan:
- Line 1 (Blue): 4 players at left hashmark (-55, 22.5)  
- Line 2 (Red): 4 players at right hashmark (-55, -22.5)
- Down middle of ice to far end (80, 0)
- Return along boards - Blue top (35), Red bottom (-35)
- Two-color system for clear distinction during simultaneous execution
- Full rink view to show complete skating flow
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

# Add src directory to path for imports
sys.path.append('src')

from hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation
from drill_utilities import *
from agent_trace_logger import start_trace, log_agent_thought

def create_u11_skating_warmup():
    """Create the U11 Skating Warm-Up drill diagram."""
    
    # Set up players for both lines at hashmarks
    players = []
    
    # LINE 1 (BLUE) - Left hashmark area 
    # Lead player with puck
    players.append(Player(
        type='forward',
        position='B1',
        coordinates={'x': -55, 'y': 22.5},  # Left hashmark
        team='home',
        has_puck=True,
        label='B1'
    ))
    
    # Queue of blue players behind lead player
    players.extend(create_player_queue(
        lead_pos={'x': -60, 'y': 22.5},  # Behind B1
        lead_label='B',
        queue_size=3,
        spacing=5,
        direction='horizontal',
        team='home',
        has_puck=False
    ))
    
    # LINE 2 (RED) - Right hashmark area
    # Lead player with puck
    players.append(Player(
        type='forward',
        position='R1',
        coordinates={'x': -55, 'y': -22.5},  # Right hashmark 
        team='away',
        has_puck=True,
        label='R1'
    ))
    
    # Queue of red players behind lead player
    players.extend(create_player_queue(
        lead_pos={'x': -60, 'y': -22.5},  # Behind R1
        lead_label='R',
        queue_size=3,
        spacing=5,
        direction='horizontal',
        team='away',
        has_puck=False
    ))
    
    # Create movements showing complete warm-up flow
    movements = []
    
    # BLUE LINE MOVEMENTS
    # 1. Skate down middle of ice from left hashmark to far end
    movements.append(Movement(
        type='skate',
        from_pos={'x': -55, 'y': 22.5},
        to_pos={'x': 80, 'y': 10},  # Slightly offset to show spread
        waypoints=[
            (-55, 22.5),   # Start at hashmark
            (-25, 20),     # Blue line area
            (0, 15),       # Center ice
            (25, 12),      # Far blue line
            (50, 11),      # Approaching end
            (80, 10)       # Far end
        ],
        style='solid',
        label='Down Middle'
    ))
    
    # 2. Return along top boards
    movements.append(Movement(
        type='skate',
        from_pos={'x': 80, 'y': 10},
        to_pos={'x': -55, 'y': 35},  # Top boards back to start area
        waypoints=[
            (80, 10),      # Far end
            (75, 25),      # Move to boards
            (50, 35),      # Along top boards
            (25, 35),      # Continue along boards
            (0, 35),       # Center area boards
            (-25, 35),     # Back toward start
            (-55, 35)      # Back to hashmark area
        ],
        style='dashed',
        label='Return - Top Boards'
    ))
    
    # 3. Return to starting position
    movements.append(Movement(
        type='skate',
        from_pos={'x': -55, 'y': 35},
        to_pos={'x': -55, 'y': 22.5},  # Back to hashmark
        style='solid',
        label='Reset'
    ))
    
    # RED LINE MOVEMENTS (mirror pattern)
    # 1. Skate down middle of ice from right hashmark to far end
    movements.append(Movement(
        type='skate',
        from_pos={'x': -55, 'y': -22.5},
        to_pos={'x': 80, 'y': -10},  # Slightly offset opposite side
        waypoints=[
            (-55, -22.5),  # Start at hashmark
            (-25, -20),    # Blue line area
            (0, -15),      # Center ice
            (25, -12),     # Far blue line
            (50, -11),     # Approaching end
            (80, -10)      # Far end
        ],
        style='solid',
        label='Down Middle'
    ))
    
    # 2. Return along bottom boards
    movements.append(Movement(
        type='skate',
        from_pos={'x': 80, 'y': -10},
        to_pos={'x': -55, 'y': -35},  # Bottom boards back to start area
        waypoints=[
            (80, -10),     # Far end
            (75, -25),     # Move to boards
            (50, -35),     # Along bottom boards
            (25, -35),     # Continue along boards
            (0, -35),      # Center area boards
            (-25, -35),    # Back toward start
            (-55, -35)     # Back to hashmark area
        ],
        style='dashed',
        label='Return - Bottom Boards'
    ))
    
    # 3. Return to starting position
    movements.append(Movement(
        type='skate',
        from_pos={'x': -55, 'y': -35},
        to_pos={'x': -55, 'y': -22.5},  # Back to hashmark
        style='solid',
        label='Reset'
    ))
    
    # Add zones for visual clarity - highlight middle ice corridor
    zones = []
    
    # Middle ice corridor zone (between faceoff circles)
    zones.append(Zone(
        type='coverage',
        shape='rectangle',
        bounds={'x': -60, 'y': -15, 'width': 140, 'height': 30},  # Full ice middle corridor
        team='neutral',
        opacity=0.05,
        color='green',
        label='Middle Ice Corridor'
    ))
    
    # Create annotations for U11 coaching points
    annotations = create_standard_annotations([
        'Two lines start at hashmarks for clear reference points',
        'Skate down middle of ice emphasizing proper stride technique',
        'Return along boards to build comfort with rink perimeter',
        'Both lines can go simultaneously or alternate as needed',
        'Focus on: Head up, full stride extension, board awareness',
        'Age-appropriate: Simple paths, fundamental skating skills'
    ], y_start=-40)
    
    # Build the complete specification
    spec = DiagramSpec(
        title='U11 - SKATING - WARM UP',
        rink={'view': 'full'},  # Full rink view to show complete warm-up flow
        players=players,
        movements=movements,
        zones=zones,
        annotations=annotations,
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'skating_warm_up',
            'skill_focus': 'basic_skating',
            'age_group': 'U11',
            'player_count': '6-8',
            'ice_time': '5-10_minutes'
        }
    )
    
    # Validate before building
    issues = validate_diagram_elements(spec)
    spatial_issues = validate_spatial_placement(spec)
    all_issues = issues + spatial_issues
    
    if all_issues:
        print("Validation issues found:")
        for issue in all_issues:
            print(f"  - {issue}")
    
    # Build and save the diagram
    builder = DiagramBuilder()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'/Users/liammckendry/hockey_coach_issue-111/hockey_diagram_mcp/outputs/drill_u11_skating_warmup_{timestamp}.png'
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Build the diagram
    builder.build(spec, output_path)
    
    # Save the specification for reference
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        json.dump(asdict(spec), f, indent=2)
    
    print(f"U11 Skating Warm-Up diagram saved to: {output_path}")
    print(f"Specification saved to: {spec_path}")
    
    return output_path, spec_path

if __name__ == "__main__":
    # Activate virtual environment and run
    import os
    print("Creating U11 - SKATING - WARM UP diagram...")
    
    try:
        create_u11_skating_warmup()
        print("✓ U11 skating warm-up diagram created successfully!")
    except Exception as e:
        print(f"Error creating diagram: {e}")
        import traceback
        traceback.print_exc()