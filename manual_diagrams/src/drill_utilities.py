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
    'zones': 6,  # Coverage areas, zones with low opacity
    'movements': 8,  # Movement lines
    'movement_arrows': 9,  # Arrow heads
    'players': 10,  # Player markers
    'equipment': 11,  # Cones, pylons, pucks
    'labels': 11,  # Player labels
    'goalie': 12,  # Goalie (higher to ensure visibility)
    'goalie_label': 13,  # Goalie label
    'annotations': 12  # Text annotations
}


def determine_view(zones_required: List[str], description: str = "") -> str:
    """
    Smart view selection with buffer zones for better readability.
    Shows adjacent zones for context without overwhelming the diagram.
    
    Args:
        zones_required: List of zones used in drill ['offensive', 'defensive', 'neutral']
        description: Original drill description for additional context
        
    Returns:
        View type: 'full', 'offensive_neutral', 'defensive_neutral', 'offensive', 'defensive'
    """
    # Check for explicit full ice mentions
    if 'full ice' in description.lower() or 'both ends' in description.lower():
        return 'full'
    
    # Determine based on zones used
    if not zones_required:
        return 'offensive'  # Default
        
    if 'full' in zones_required or len(zones_required) > 2:
        return 'full'
    elif len(zones_required) == 2:
        # Two zones: show all three for clarity
        return 'full'
    elif len(zones_required) == 1:
        # Single zone: show zone + neutral for context
        zone = zones_required[0]
        if zone == 'offensive':
            return 'offensive'  # Note: sportypy may need 'offensive_neutral' custom view
        elif zone == 'defensive':
            return 'defensive'  # Note: sportypy may need 'defensive_neutral' custom view
        elif zone == 'neutral':
            return 'neutral'
    
    return 'offensive'  # Safe default


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
    # Queue positions (off boards for visibility)
    'left_queue': {'x': -20, 'y': -38},    # Off boards, left side
    'right_queue': {'x': 20, 'y': 38},      # Off boards, right side
    'neutral_queue_left': {'x': 10, 'y': 38},   # Neutral zone queue
    'neutral_queue_right': {'x': 10, 'y': -38},  # Neutral zone queue
    
    # Coach positions
    'left_coach': {'x': -69, 'y': 35},      # Near boards, not at face-off dot
    'right_coach': {'x': 69, 'y': -35},     # Near boards, not at face-off dot
    'coach_blue_line_left': {'x': -25, 'y': 35},   # On blue line
    'coach_blue_line_right': {'x': 25, 'y': -35},  # On blue line
    'coach_inside_zone_left': {'x': -30, 'y': 35},  # Inside zone
    'coach_inside_zone_right': {'x': 30, 'y': -35}, # Inside zone
    
    # Goal positions
    'left_goal': {'x': -83, 'y': 0},        # In crease
    'right_goal': {'x': 83, 'y': 0},        # In crease
    'second_net': {'x': 55, 'y': 0},        # Second net position for small area games
    
    # Slot/shooting positions
    'left_slot': {'x': -75, 'y': 5},        # Hashmarks/mid-slot
    'right_slot': {'x': 75, 'y': -5},       # Hashmarks/mid-slot
    'left_high_slot': {'x': -60, 'y': 0},   # High slot
    'right_high_slot': {'x': 60, 'y': 0},   # High slot
    
    # Faceoff positions
    'center_ice': {'x': 0, 'y': 0},         # Center of rink
    'left_circle_center': {'x': -69, 'y': 22.5},   # Left offensive circle center
    'right_circle_center': {'x': 69, 'y': -22.5},  # Right offensive circle center
    'left_defensive_circle': {'x': -69, 'y': -22.5},  # Left defensive circle
    'right_defensive_circle': {'x': 69, 'y': 22.5},   # Right defensive circle
    
    # Corner positions
    'left_corner_top': {'x': -85, 'y': 38},
    'left_corner_bottom': {'x': -85, 'y': -38},
    'right_corner_top': {'x': 85, 'y': 38},
    'right_corner_bottom': {'x': 85, 'y': -38},
    
    # Blue line positions
    'blue_line_left': {'x': -25, 'y': 0},
    'blue_line_right': {'x': 25, 'y': 0},
    
    # Board positions
    'left_boards_center': {'x': -100, 'y': 0},
    'right_boards_center': {'x': 100, 'y': 0},
    'top_boards_center': {'x': 0, 'y': 42.5},
    'bottom_boards_center': {'x': 0, 'y': -42.5}
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

# Landmark reference system for natural language mapping
LANDMARKS = {
    'goal_lines': {'x': [89, -89]},  # Goal line x-coordinates
    'blue_lines': {'x': [25, -25]},  # Blue line x-coordinates
    'red_line': {'x': 0},  # Center red line
    'faceoff_circles': {  # Faceoff circle centers and radius
        'left_offensive': {'center': (-69, 22.5), 'radius': 15},
        'right_offensive': {'center': (69, -22.5), 'radius': 15},
        'left_defensive': {'center': (-69, -22.5), 'radius': 15},
        'right_defensive': {'center': (69, 22.5), 'radius': 15},
        'center': {'center': (0, 0), 'radius': 15}
    },
    'boards': {'y': [42.5, -42.5]},  # Board y-coordinates
    'crease': {'left': {'x': -89, 'radius': 6}, 'right': {'x': 89, 'radius': 6}},
    'slot': {'left': {'x_range': [-80, -60], 'y_range': [-10, 10]}, 
             'right': {'x_range': [60, 80], 'y_range': [-10, 10]}},
    'house': {'left': {'x_range': [-89, -60]}, 'right': {'x_range': [60, 89]}},
    'neutral_zone': {'x_range': [-25, 25]}
}

def map_description_to_position(description: str) -> Dict[str, float]:
    """
    Map natural language position descriptions to coordinates.
    
    Args:
        description: Natural language description like "top corner", "bottom of circle", etc.
    
    Returns:
        Dictionary with 'x' and 'y' coordinates
    """
    description = description.lower()
    
    # Corner positions
    if "corner" in description:
        if "left" in description or "defensive" in description:
            if "top" in description or "near" in description:
                return STANDARD_POSITIONS['left_corner_top']
            else:
                return STANDARD_POSITIONS['left_corner_bottom']
        elif "right" in description or "offensive" in description:
            if "top" in description or "near" in description:
                return STANDARD_POSITIONS['right_corner_top']
            else:
                return STANDARD_POSITIONS['right_corner_bottom']
    
    # Circle positions
    if "circle" in description or "faceoff" in description:
        if "bottom" in description:
            y_offset = -7.5  # Below circle center
        elif "top" in description:
            y_offset = 7.5  # Above circle center
        else:
            y_offset = 0  # Circle center
        
        if "left" in description:
            base = STANDARD_POSITIONS['left_circle_center']
            return {'x': base['x'], 'y': base['y'] + y_offset}
        elif "right" in description:
            base = STANDARD_POSITIONS['right_circle_center']
            return {'x': base['x'], 'y': base['y'] + y_offset}
    
    # Slot positions
    if "slot" in description:
        if "high" in description:
            return STANDARD_POSITIONS['left_high_slot'] if "left" in description else STANDARD_POSITIONS['right_high_slot']
        else:
            return STANDARD_POSITIONS['left_slot'] if "left" in description else STANDARD_POSITIONS['right_slot']
    
    # Blue line positions
    if "blue line" in description:
        return STANDARD_POSITIONS['blue_line_left'] if "left" in description else STANDARD_POSITIONS['blue_line_right']
    
    # Center ice
    if "center" in description:
        return STANDARD_POSITIONS['center_ice']
    
    # Default to center if no match
    return {'x': 0, 'y': 0}

def create_equipment_zone(equipment_type: str, position: Dict[str, float], 
                         size: float = 2.0):
    """
    Create equipment zones (pylons, cones, etc.) with proper styling.
    
    Args:
        equipment_type: 'cone', 'pylon', 'marker'
        position: {'x': x, 'y': y} position
        size: Size of the equipment
    
    Returns:
        Zone object representing the equipment
    """
    from hockey_diagram_builder import Zone
    
    if equipment_type in ['cone', 'pylon']:
        # Create triangle vertices for cone/pylon
        vertices = [
            (position['x'], position['y'] + size),  # Top point
            (position['x'] - size, position['y'] - size),  # Bottom left
            (position['x'] + size, position['y'] - size)   # Bottom right
        ]
        
        return Zone(
            type='equipment',
            shape='polygon',
            bounds={'vertices': vertices},
            team='neutral',
            opacity=1.0,
            color='darkorange',
            label=''
        )
    
    elif equipment_type == 'marker':
        return Zone(
            type='equipment',
            shape='circle',
            bounds={'x': position['x'], 'y': position['y'], 'radius': size},
            team='neutral',
            opacity=0.8,
            color='yellow',
            label=''
        )
    
    return None

def create_puck_at_position(position: Dict[str, float], label: str = '') -> Player:
    """
    Create a puck at the specified position.
    
    Args:
        position: {'x': x, 'y': y} position
        label: Optional label for the puck
    
    Returns:
        Player object of type 'puck'
    """
    return Player(
        type='puck',
        position='puck',
        coordinates=position,
        team='neutral',
        has_puck=False,
        label=label
    )

def create_smooth_path_with_waypoints(start: Dict, end: Dict, 
                                     waypoints: List[Tuple[float, float]] = None,
                                     num_interpolation_points: int = 100) -> List[Tuple[float, float]]:
    """
    Create a smooth path using cubic spline interpolation through waypoints.
    
    Args:
        start: Starting position {'x': x, 'y': y}
        end: Ending position {'x': x, 'y': y}
        waypoints: Optional list of (x, y) tuples for intermediate points
        num_interpolation_points: Number of points for smooth curve
    
    Returns:
        List of (x, y) tuples representing the smooth path
    """
    try:
        from scipy.interpolate import CubicSpline
        import numpy as np
        
        # Build complete path
        path_points = [(start['x'], start['y'])]
        if waypoints:
            path_points.extend(waypoints)
        path_points.append((end['x'], end['y']))
        
        # Extract x and y coordinates
        x_coords = [p[0] for p in path_points]
        y_coords = [p[1] for p in path_points]
        
        # Create parameter t for each point
        t = np.linspace(0, 1, len(path_points))
        
        # Create cubic splines for x and y
        cs_x = CubicSpline(t, x_coords)
        cs_y = CubicSpline(t, y_coords)
        
        # Generate smooth path
        t_smooth = np.linspace(0, 1, num_interpolation_points)
        x_smooth = cs_x(t_smooth)
        y_smooth = cs_y(t_smooth)
        
        return [(float(x), float(y)) for x, y in zip(x_smooth, y_smooth)]
        
    except ImportError:
        # Fallback to linear interpolation if scipy not available
        if waypoints:
            all_points = [start] + list(waypoints) + [end]
        else:
            all_points = [start, end]
        return [(p['x'] if isinstance(p, dict) else p[0], 
                 p['y'] if isinstance(p, dict) else p[1]) for p in all_points]

def parse_movement_description(description: str) -> Dict[str, any]:
    """
    Parse natural language movement descriptions to movement parameters.
    
    Args:
        description: Natural language like "cross ice", "around pylon", "loop around circle"
    
    Returns:
        Dictionary with movement type, style, and any special parameters
    """
    description = description.lower()
    
    # Movement types
    if any(word in description for word in ['pass', 'sauce']):
        return {'type': 'pass', 'style': 'dotted'}
    elif any(word in description for word in ['shoot', 'shot']):
        return {'type': 'shot', 'style': 'dashed'}
    elif any(word in description for word in ['carry', 'puck']):
        return {'type': 'carry', 'style': 'solid', 'with_puck': True}
    elif any(word in description for word in ['backward', 'back']):
        return {'type': 'backward', 'style': 'wavy'}
    elif any(word in description for word in ['pressure', 'defend', 'angle']):
        return {'type': 'pressure', 'style': 'solid'}
    else:
        return {'type': 'skate', 'style': 'solid'}

def validate_diagram_elements(spec) -> List[str]:
    """
    Validate diagram elements for common issues found during iterations.
    
    Args:
        spec: DiagramSpec object to validate
    
    Returns:
        List of validation warnings/errors
    """
    issues = []
    
    # Check z-order values
    for player in spec.players:
        if player.type == 'goalie' and not hasattr(player, '_z_order'):
            issues.append("Goalie should have z-order 12 for visibility")
    
    # Check equipment placement
    equipment_positions = []
    player_positions = [(p.coordinates['x'], p.coordinates['y']) for p in spec.players]
    
    for zone in spec.zones:
        if zone.type == 'equipment':
            pos = (zone.bounds.get('x', 0), zone.bounds.get('y', 0))
            equipment_positions.append(pos)
            
            # Check if equipment is on top of players
            for p_pos in player_positions:
                dist = ((pos[0] - p_pos[0])**2 + (pos[1] - p_pos[1])**2)**0.5
                if dist < 2:
                    issues.append(f"Equipment at {pos} too close to player at {p_pos}")
    
    # Check for counterclockwise arc issues
    for movement in spec.movements:
        if hasattr(movement, 'arc_params'):
            start, end = movement.arc_params.get('start_angle'), movement.arc_params.get('end_angle')
            if start and end and end < start:
                issues.append(f"Arc from {start}° to {end}° needs 360° adjustment for counterclockwise")
    
    # Check cross-ice movements have sufficient Y-axis change
    for movement in spec.movements:
        if isinstance(movement.from_pos, dict) and isinstance(movement.to_pos, dict):
            y_change = abs(movement.to_pos['y'] - movement.from_pos['y'])
            x_change = abs(movement.to_pos['x'] - movement.from_pos['x'])
            if movement.label and 'cross' in movement.label.lower() and y_change < 20:
                issues.append(f"Cross-ice movement needs larger Y-axis change (currently {y_change})")
    
    return issues


def validate_spatial_placement(spec) -> List[str]:
    """
    Comprehensive spatial validation to prevent collisions and placement issues.
    Checks player-to-player, player-to-boards, player-to-equipment spacing.
    
    Args:
        spec: DiagramSpec object to validate
        
    Returns:
        List of spatial conflict issues found
    """
    issues = []
    
    def calculate_distance(pos1, pos2):
        """Calculate Euclidean distance between two positions"""
        x1 = pos1.get('x', 0) if isinstance(pos1, dict) else pos1[0]
        y1 = pos1.get('y', 0) if isinstance(pos1, dict) else pos1[1]
        x2 = pos2.get('x', 0) if isinstance(pos2, dict) else pos2[0]
        y2 = pos2.get('y', 0) if isinstance(pos2, dict) else pos2[1]
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    
    # 1. Player-to-player spacing (minimum 3 units)
    for i, p1 in enumerate(spec.players):
        for j, p2 in enumerate(spec.players[i+1:], i+1):
            dist = calculate_distance(p1.coordinates, p2.coordinates)
            if dist < 3:
                issues.append(f"Players {p1.label}({i}) and {p2.label}({j}) too close ({dist:.1f} units, min 3)")
    
    # 2. Player-to-boards spacing (minimum 2 units from edge)
    board_limit = 40.5  # Standard rink half-width is 42.5, leave 2 unit buffer
    for player in spec.players:
        y_pos = player.coordinates.get('y', 0)
        x_pos = player.coordinates.get('x', 0)
        
        # Check side boards
        if abs(y_pos) > board_limit:
            issues.append(f"Player {player.label} too close to boards (y={y_pos:.1f}, max ±{board_limit})")
        
        # Check end boards (if in offensive/defensive zone)
        if abs(x_pos) > 87:  # 89 is goal line, leave 2 unit buffer
            issues.append(f"Player {player.label} too close to end boards (x={x_pos:.1f}, max ±87)")
    
    # 3. Equipment-to-player spacing (minimum 4 units)
    for zone in spec.zones:
        if zone.type == 'equipment' or (hasattr(zone, 'label') and 'cone' in zone.label.lower()):
            # Get equipment position
            if hasattr(zone, 'bounds'):
                equip_pos = {'x': zone.bounds.get('x', 0), 'y': zone.bounds.get('y', 0)}
            elif hasattr(zone, 'center'):
                equip_pos = zone.center
            else:
                continue
                
            for player in spec.players:
                dist = calculate_distance(equip_pos, player.coordinates)
                if dist < 4:
                    issues.append(f"Player {player.label} too close to equipment ({dist:.1f} units, min 4)")
    
    # 4. Label collision detection (estimate based on proximity)
    label_positions = []
    for player in spec.players:
        if player.label:
            # Account for label offset if present
            label_x = player.coordinates['x']
            label_y = player.coordinates['y']
            if hasattr(player, 'label_offset'):
                label_x += player.label_offset.get('x', 0)
                label_y += player.label_offset.get('y', 0)
            label_positions.append((label_x, label_y, player.label))
    
    # Check label spacing (minimum 5 units for readability)
    for i, (x1, y1, label1) in enumerate(label_positions):
        for x2, y2, label2 in label_positions[i+1:]:
            dist = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            if dist < 5:
                issues.append(f"Labels '{label1}' and '{label2}' may overlap ({dist:.1f} units apart, min 5)")
    
    # 5. Movement path validation (check if paths cross through equipment)
    for movement in spec.movements:
        if hasattr(movement, 'waypoints') and movement.waypoints:
            for zone in spec.zones:
                if zone.type == 'equipment':
                    equip_pos = {'x': zone.bounds.get('x', 0), 'y': zone.bounds.get('y', 0)}
                    # Check if any waypoint is too close to equipment
                    for waypoint in movement.waypoints:
                        wp_pos = {'x': waypoint[0], 'y': waypoint[1]} if isinstance(waypoint, tuple) else waypoint
                        dist = calculate_distance(equip_pos, wp_pos)
                        if dist < 3:
                            issues.append(f"Movement path passes too close to equipment ({dist:.1f} units)")
                            break
    
    return issues