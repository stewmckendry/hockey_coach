#!/usr/bin/env python
"""
Drill 3: SMOOTH CURVED PATHS VERSION
Using spline interpolation for natural hockey movements
Created: 2025-08-27 (Iteration 5)

Implements truly smooth skating paths using cubic splines.
"""

import sys
import numpy as np
from datetime import datetime
from pathlib import Path
from scipy.interpolate import CubicSpline
sys.path.append('..')

from hockey_diagram_builder import DiagramBuilder, DiagramSpec, Player, Movement, Zone, Annotation
from drill_utilities import generate_arc_points, STANDARD_POSITIONS, Z_ORDER


def create_smooth_movement(waypoints, movement_type='skate', label='', with_puck=False):
    """
    Create a single smooth movement through waypoints.
    Returns a Movement object with 'curved_path' data.
    """
    # Create a special movement type that indicates it should use curved path
    movement = Movement(
        type=movement_type,
        from_pos={'x': waypoints[0][0], 'y': waypoints[0][1]},
        to_pos={'x': waypoints[-1][0], 'y': waypoints[-1][1]},
        style='solid' if movement_type in ['carry', 'pressure'] else 'dashed' if movement_type == 'skate' else 'dotted',
        with_puck=with_puck,
        label=label
    )
    # Add waypoints as a custom field (we'll modify the builder to use this)
    movement.waypoints = waypoints
    return movement


def create_phase1_smooth(output_path=None):
    """Phase 1: Dump-in with SMOOTH movements"""
    
    spec = DiagramSpec(
        title='Drill 3 - Phase 1: Dump-in (Smooth Paths)',
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
                   
            Player(type='puck', position='Puck', coordinates={'x': -85, 'y': 35},
                   team='neutral', has_puck=False),
        ],
        movements=[],
        zones=[],
        annotations=[
            Annotation(text='PHASE 1: Smooth Movement Paths', position={'x': 0, 'y': 38},
                      size='large', style='bold'),
            Annotation(text='All movements use natural curves', position={'x': 0, 'y': 35},
                      size='small', style='normal'),
        ],
        metadata={
            'created': datetime.now().isoformat(),
            'category': 'drill',
            'phase': 1,
            'version': 'smooth'
        }
    )

    movements = []
    
    # Coach dumps puck (straight line is fine for passes)
    movements.append(Movement(type='pass', from_pos={'x': 10, 'y': 0},
                             to_pos={'x': -85, 'y': 35}, style='dotted', label='Dump'))
    
    # For actual smooth implementation, we need to modify how movements are drawn
    # Let's create a custom movement type with waypoints
    
    # RD to puck - single smooth curve
    rd_waypoints = [
        (-25, 15),     # Start
        (-45, 20),     # Control point 1
        (-65, 28),     # Control point 2
        (-80, 33),     # Near puck
        (-82, 30),     # Curl point
        (-78, 28)      # Final position
    ]
    movements.append(create_smooth_movement(rd_waypoints, 'skate', 'To puck'))
    
    # LD to net front - single smooth curve
    ld_waypoints = [
        (-25, -15),    # Start
        (-45, -10),    # Control point
        (-65, -5),     # Control point
        (-78, 2),      # Net front
        (-80, 5),      # Curl
        (-78, 5)       # Final
    ]
    movements.append(create_smooth_movement(ld_waypoints, 'skate', 'Net front'))
    
    # LW to hashmarks - smooth curve
    lw_waypoints = [
        (0, 22.5),     # Start
        (-25, 28),     # Control
        (-50, 35),     # Control
        (-69, 38),     # Hashmarks
        (-72, 35),     # Curl
        (-69, 36)      # Final
    ]
    movements.append(create_smooth_movement(lw_waypoints, 'skate', 'Hashmarks'))
    
    # Centre support curl - smooth arc around dot
    c_waypoints = [
        (0, 0),        # Start
        (-25, 8),      # Entry
        (-50, 15),     # Approach
        (-65, 20),     # Around dot
        (-69, 22.5),   # Dot position
        (-72, 20),     # Curl around
        (-70, 18),     # Complete
        (-65, 20)      # Support position
    ]
    movements.append(create_smooth_movement(c_waypoints, 'skate', 'Support'))
    
    # RW to middle - smooth curve
    rw_waypoints = [
        (0, -22.5),    # Start
        (-25, -15),    # Entry
        (-45, -5),     # Middle approach
        (-50, 0),      # Middle ice
        (-52, 3),      # Curl
        (-50, 2)       # Final
    ]
    movements.append(create_smooth_movement(rw_waypoints, 'skate', 'Middle'))

    spec.movements = movements
    
    # We need a custom builder that handles smooth paths
    builder = SmoothDiagramBuilder()
    
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'../../outputs/drill3_phase1_smooth_{timestamp}.png'
    
    result = builder.build(spec, output_path)
    spec_path = output_path.replace('.png', '_spec.json')
    with open(spec_path, 'w') as f:
        f.write(builder.spec_to_json(spec))
    
    print(f'Smooth Phase 1 created: {result}')
    return result, spec_path


class SmoothDiagramBuilder(DiagramBuilder):
    """Extended diagram builder that handles smooth curved paths"""
    
    def _draw_movements(self, movements):
        """Override to handle smooth movements with waypoints"""
        for movement in movements:
            # Check if this movement has waypoints for smooth curve
            if hasattr(movement, 'waypoints') and len(movement.waypoints) > 2:
                self._draw_smooth_movement(movement)
            else:
                # Use regular movement drawing for passes and simple movements
                super()._draw_movements([movement])
    
    def _draw_smooth_movement(self, movement):
        """Draw a smooth curved movement using cubic spline"""
        waypoints = np.array(movement.waypoints)
        
        # Create parameter t for interpolation
        t = np.arange(len(waypoints))
        
        # Create cubic splines for x and y
        cs_x = CubicSpline(t, waypoints[:, 0])
        cs_y = CubicSpline(t, waypoints[:, 1])
        
        # Generate smooth curve with many points
        t_smooth = np.linspace(0, len(waypoints)-1, 100)
        x_smooth = cs_x(t_smooth)
        y_smooth = cs_y(t_smooth)
        
        # Determine line style and color
        if movement.type == 'carry':
            linestyle = '-'
            linewidth = 3
            color = 'black'
        elif movement.type == 'pass':
            linestyle = ':'
            linewidth = 2
            color = 'black'
        elif movement.type == 'shot':
            linestyle = '--'
            linewidth = 2.5
            color = 'black'
        elif movement.type == 'pressure':
            linestyle = '-'
            linewidth = 4
            color = 'black'
            alpha = 0.7
        else:  # skate
            linestyle = '-'
            linewidth = 2
            color = 'gray'
        
        # Draw the smooth curve
        self.ax.plot(x_smooth, y_smooth, 
                    linestyle=linestyle, 
                    linewidth=linewidth, 
                    color=color, 
                    alpha=0.8, 
                    zorder=8)
        
        # Add arrowhead at the end
        if len(x_smooth) > 5:
            dx = x_smooth[-1] - x_smooth[-5]
            dy = y_smooth[-1] - y_smooth[-5]
            self.ax.arrow(x_smooth[-5], y_smooth[-5], dx*0.8, dy*0.8,
                         head_width=1.5, head_length=1, 
                         fc=color, ec=color, 
                         zorder=9, alpha=0.8)
        
        # Add label if specified
        if movement.label:
            # Find a good position for the label (middle of path)
            mid_idx = len(x_smooth) // 2
            self.ax.text(x_smooth[mid_idx], y_smooth[mid_idx] + 2, 
                        movement.label,
                        fontsize=8, ha='center', 
                        style='italic', zorder=9)
        
        # Add puck indicator if with_puck
        if movement.with_puck:
            # Add small puck dots along the path
            puck_indices = np.linspace(10, len(x_smooth)-10, 5, dtype=int)
            for idx in puck_indices:
                self.ax.plot(x_smooth[idx], y_smooth[idx], 
                           'ko', markersize=3, zorder=10)


def create_all_smooth_phases():
    """Create all phases with smooth movements"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("\nCreating Smooth Movement Drill 3...")
    print("-" * 50)
    
    # For now, just create Phase 1 as demonstration
    result = create_phase1_smooth(f'../../outputs/drill3_phase1_smooth_{timestamp}.png')
    
    print(f"\n✓ Created smooth movement diagram")
    print(f"✓ Timestamp: {timestamp}")
    return result


if __name__ == "__main__":
    create_all_smooth_phases()