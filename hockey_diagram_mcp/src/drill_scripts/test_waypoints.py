#!/usr/bin/env python
"""
Test the new waypoints feature in DiagramBuilder
"""

import sys
from datetime import datetime
sys.path.append('..')

from hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation

def test_waypoints():
    """Test diagram with smooth curved movements using waypoints"""
    
    spec = DiagramSpec(
        title='Test: Smooth Curved Movements with Waypoints',
        rink={'view': 'full'},
        players=[
            Player(type='forward', position='F1', coordinates={'x': -25, 'y': -20},
                   team='home', has_puck=True, label='F1'),
            Player(type='defense', position='D1', coordinates={'x': 25, 'y': 20},
                   team='away', has_puck=False, label='D1'),
            Player(type='goalie', position='G', coordinates={'x': 83, 'y': 0},
                   team='away', label='G'),
        ],
        movements=[
            # Traditional straight line movement (no waypoints)
            Movement(
                type='pass',
                from_pos={'x': -25, 'y': -20},
                to_pos={'x': 25, 'y': 20},
                style='dotted',
                label='Straight Pass'
            ),
            
            # New smooth curved movement with waypoints
            Movement(
                type='skate',
                from_pos={'x': -25, 'y': -20},
                to_pos={'x': 75, 'y': 0},
                style='solid',
                label='Smooth Skate',
                waypoints=[
                    (-25, -20),  # Start
                    (0, -15),    # Waypoint 1
                    (25, -5),    # Waypoint 2
                    (50, 5),     # Waypoint 3
                    (75, 0)      # End
                ]
            ),
            
            # Curved carry with puck
            Movement(
                type='carry',
                from_pos={'x': 25, 'y': 20},
                to_pos={'x': -50, 'y': -10},
                style='solid',
                with_puck=True,
                label='Carry with curl',
                waypoints=[
                    (25, 20),    # Start
                    (10, 25),    # Curl up
                    (-10, 20),   # Continue
                    (-30, 10),   # Turn down
                    (-40, -5),   # Continue
                    (-50, -10)   # End
                ]
            ),
        ],
        zones=[],
        annotations=[
            Annotation(text='Testing Waypoints Feature', position={'x': 0, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='• Straight line (no waypoints)', position={'x': 0, 'y': 35},
                      size='small', style='normal'),
            Annotation(text='• Smooth curve (with waypoints)', position={'x': 0, 'y': 33},
                      size='small', style='normal'),
            Annotation(text='• Carry shows puck dots', position={'x': 0, 'y': 31},
                      size='small', style='normal'),
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'test': 'waypoints_feature'
        }
    )
    
    builder = DiagramBuilder()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'../../outputs/test_waypoints_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    print(f'Test diagram created: {result}')
    
    # Also save the spec for reference
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    print(f'Spec saved: {spec_path}')
    
    return result, spec_path

if __name__ == "__main__":
    test_waypoints()