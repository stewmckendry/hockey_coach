"""
Reusable utilities for hockey drill diagram creation.
Extracted from lessons learned during Drill 1 development (16 iterations).
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from hockey_diagram_builder import Movement, Player, Annotation


# Standard Z-order values for proper layering
Z_ORDER = {
    'rink': 0,  # Base layer
    'zones': 8,
    'movements': 9,
    'players': 10,
    'labels': 11,
    'annotations': 12
}


def generate_arc_points(center_x: float, center_y: float, radius: float, 
                       start_angle: float, end_angle: float, 
                       num_points: int = 15) -> List[Tuple[float, float]]:
    """
    Generate points along a circle arc ensuring counterclockwise direction.
    
    This is a critical utility discovered through iterations - when end_angle
    is less than start_angle, we must add 360° to ensure counterclockwise movement.
    
    Args:
        center_x: X coordinate of circle center
        center_y: Y coordinate of circle center
        radius: Radius of the circle
        start_angle: Starting angle in degrees (0° = right, 90° = top)
        end_angle: Ending angle in degrees
        num_points: Number of points to generate along the arc
    
    Returns:
        List of (x, y) coordinate tuples along the arc
    """
    # Critical fix for counterclockwise movement
    if end_angle <= start_angle:
        end_angle += 360
    
    angles = np.linspace(np.radians(start_angle), np.radians(end_angle), num_points)
    x_points = center_x + radius * np.cos(angles)
    y_points = center_y + radius * np.sin(angles)
    return [(float(x), float(y)) for x, y in zip(x_points, y_points)]


def create_crossover_movements(start_pos: Dict, entry_angle: float, exit_angle: float,
                               radius: float = 17, label_position: int = 4) -> List[Movement]:
    """
    Create a series of crossover movements around a circle.
    
    Args:
        start_pos: Starting position {'x': x, 'y': y}
        entry_angle: Angle to enter the circle (degrees)
        exit_angle: Angle to exit the circle (degrees)
        radius: Radius of the circle (default 17 for outside face-off circle)
        label_position: Which segment to label with "Crossovers"
    
    Returns:
        List of Movement objects for the crossover pattern
    """
    movements = []
    
    # 1. Approach to circle
    entry_x = radius * np.cos(np.radians(entry_angle))
    entry_y = radius * np.sin(np.radians(entry_angle))
    movements.append(Movement(
        type='skate',
        from_pos=start_pos,
        to_pos={'x': entry_x, 'y': entry_y},
        style='solid',
        label=''
    ))
    
    # 2. Arc around circle
    arc_points = generate_arc_points(0, 0, radius, entry_angle, exit_angle, 10)
    for i in range(len(arc_points) - 1):
        label = 'Crossovers' if i == label_position else ''
        movements.append(Movement(
            type='skate',
            from_pos={'x': arc_points[i][0], 'y': arc_points[i][1]},
            to_pos={'x': arc_points[i+1][0], 'y': arc_points[i+1][1]},
            style='dashed',
            label=label
        ))
    
    return movements


def calculate_trajectory_points(start_pos: Dict, end_pos: Dict, 
                               ratios: List[float] = [0.33, 0.66]) -> List[Dict]:
    """
    Calculate intermediate points along a straight trajectory.
    Useful for determining pass/receive points along a skating path.
    
    Args:
        start_pos: Starting position {'x': x, 'y': y}
        end_pos: Ending position {'x': x, 'y': y}
        ratios: List of ratios for intermediate points (0.33 = 1/3, 0.66 = 2/3)
    
    Returns:
        List of intermediate positions
    """
    points = []
    for ratio in ratios:
        x = start_pos['x'] + (end_pos['x'] - start_pos['x']) * ratio
        y = start_pos['y'] + (end_pos['y'] - start_pos['y']) * ratio
        points.append({'x': x, 'y': y})
    return points


def create_player_queue(lead_pos: Dict, lead_label: str, queue_size: int = 2,
                       spacing: int = 5, direction: str = 'horizontal',
                       team: str = 'home', has_puck: bool = False) -> List[Player]:
    """
    Create a queue of players for drill starting positions.
    
    Args:
        lead_pos: Position of the lead player {'x': x, 'y': y}
        lead_label: Label for the lead player (e.g., 'X1')
        queue_size: Number of additional players in queue
        spacing: Units between players
        direction: 'horizontal' or 'vertical' queue
        team: 'home' or 'away'
        has_puck: Whether lead player has puck
    
    Returns:
        List of Player objects for the queue
    """
    players = []
    
    # Lead player
    players.append(Player(
        type='forward',
        position=lead_label,
        coordinates=lead_pos,
        team=team,
        has_puck=has_puck,
        label=lead_label
    ))
    
    # Queue players
    for i in range(queue_size):
        if direction == 'horizontal':
            x = lead_pos['x'] - (spacing * (i + 1))
            y = lead_pos['y']
        else:
            x = lead_pos['x']
            y = lead_pos['y'] - (spacing * (i + 1))
        
        players.append(Player(
            type='forward',
            position='X',
            coordinates={'x': x, 'y': y},
            team=team,
            has_puck=False,
            label='X'
        ))
    
    return players


def create_pass_sequence(positions: List[Dict], coach_pos: Dict, 
                        pass_point_idx: int = 0, receive_point_idx: int = 1,
                        shoot_pos: Dict = None, goal_pos: Dict = None) -> List[Movement]:
    """
    Create a standard pass-receive-shoot sequence.
    
    Args:
        positions: List of positions along the path
        coach_pos: Coach position for pass/receive
        pass_point_idx: Index in positions for pass point
        receive_point_idx: Index in positions for receive point
        shoot_pos: Shooting position (if None, uses last position)
        goal_pos: Goal position for shot
    
    Returns:
        List of Movement objects for the sequence
    """
    movements = []
    
    if shoot_pos is None:
        shoot_pos = positions[-1]
    
    # Skate to pass point
    if pass_point_idx > 0:
        movements.append(Movement(
            type='skate',
            from_pos=positions[pass_point_idx - 1],
            to_pos=positions[pass_point_idx],
            style='solid'
        ))
    
    # Pass to coach
    movements.append(Movement(
        type='pass',
        from_pos=positions[pass_point_idx],
        to_pos=coach_pos,
        style='dotted',
        label='Pass'
    ))
    
    # Continue to receive point
    movements.append(Movement(
        type='skate',
        from_pos=positions[pass_point_idx],
        to_pos=positions[receive_point_idx],
        style='solid'
    ))
    
    # Receive pass
    movements.append(Movement(
        type='pass',
        from_pos=coach_pos,
        to_pos=positions[receive_point_idx],
        style='dotted',
        label='Receive'
    ))
    
    # Carry to shooting position
    movements.append(Movement(
        type='carry',
        from_pos=positions[receive_point_idx],
        to_pos=shoot_pos,
        style='solid',
        with_puck=True
    ))
    
    # Shoot
    if goal_pos:
        movements.append(Movement(
            type='shot',
            from_pos=shoot_pos,
            to_pos=goal_pos,
            style='dashed',
            label='Shot'
        ))
    
    return movements


# Standard positions (discovered through iterations)
STANDARD_POSITIONS = {
    'left_queue': {'x': -20, 'y': -38},    # Off boards, left side
    'right_queue': {'x': 20, 'y': 38},      # Off boards, right side
    'left_coach': {'x': -69, 'y': 35},      # Near boards, not at face-off dot
    'right_coach': {'x': 69, 'y': -35},     # Near boards, not at face-off dot
    'left_goal': {'x': -83, 'y': 0},        # In crease
    'right_goal': {'x': 83, 'y': 0},        # In crease
    'left_slot': {'x': -75, 'y': 5},        # Hashmarks/mid-slot
    'right_slot': {'x': 75, 'y': -5},       # Hashmarks/mid-slot
    'center_ice': {'x': 0, 'y': 0},         # Center of rink
}

# Standard drill annotations
def create_standard_annotations(key_points: List[str], y_start: int = -35) -> List[Annotation]:
    """
    Create standard drill annotations with key points.
    
    Args:
        key_points: List of key point strings
        y_start: Starting y position for annotations
    
    Returns:
        List of Annotation objects
    """
    annotations = [
        Annotation(
            text='Key Points:',
            position={'x': 0, 'y': y_start},
            size='medium',
            style='bold'
        )
    ]
    
    for i, point in enumerate(key_points):
        annotations.append(Annotation(
            text=f'• {point}',
            position={'x': 0, 'y': y_start - (i + 1) * 2},
            size='small',
            style='normal'
        ))
    
    return annotations


# Angle reference constants
ANGLES = {
    'right': 0,
    'top': 90,
    'left': 180,
    'bottom': 270,
    'top_right': 45,
    'top_left': 135,
    'bottom_left': 225,
    'bottom_right': 315,
    # Offset angles for visual clarity
    'offset_bottom': 315,  # Instead of 270
    'offset_top': 135,     # Instead of 90
}