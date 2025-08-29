"""
Position mapping utilities for hockey diagrams.
Converts natural language positions to coordinates.
Coordinate system: x: -100 to 100 (left to right), y: -42.5 to 42.5 (bottom to top)
"""

from typing import Dict, Any, Optional, List, Tuple, Union
import math
import re

# Position mappings by zone
OFFENSIVE_POSITIONS = {
    # Faceoff dots
    "left faceoff dot": (-69, 22.5),
    "right faceoff dot": (-69, -22.5),
    "left dot": (-69, 22.5),
    "right dot": (-69, -22.5),
    
    # Net area
    "behind net": (-89, 0),
    "behind the net": (-89, 0),
    "net front": (-86, 0),
    "in front of net": (-86, 0),
    "crease": (-86, 0),
    "left post": (-89, 6),
    "right post": (-89, -6),
    
    # Slot area
    "slot": (-69, 0),
    "high slot": (-50, 0),
    "low slot": (-75, 0),
    
    # Hash marks
    "left hash": (-75, 22.5),
    "right hash": (-75, -22.5),
    "left hash marks": (-75, 22.5),
    "right hash marks": (-75, -22.5),
    
    # Corners
    "left corner": (-89, 36),
    "right corner": (-89, -36),
    
    # Half wall
    "left half wall": (-69, 38),
    "right half wall": (-69, -38),
    "half wall": (-69, 38),  # Default to left
    
    # Blue line/points
    "left point": (-25, 20),
    "right point": (-25, -20),
    "point": (-25, 0),
    "blue line": (-25, 0),
    "offensive blue line": (-25, 0),
    
    # Goal line
    "goal line": (-89, 0),
    "goal line extended": (-89, 38),
    
    # Queue positions (off ice for visibility)
    "left queue": (-20, -38),
    "right queue": (-20, 38),
    "corner queue left": (-75, -38),
    "corner queue right": (-75, 38),
}

DEFENSIVE_POSITIONS = {
    # Faceoff dots
    "left faceoff dot": (69, 22.5),
    "right faceoff dot": (69, -22.5),
    "left dot": (69, 22.5),
    "right dot": (69, -22.5),
    
    # Net area
    "behind net": (89, 0),
    "behind the net": (89, 0),
    "net front": (86, 0),
    "in front of net": (86, 0),
    "crease": (86, 0),
    "left post": (89, 6),
    "right post": (89, -6),
    
    # Slot area
    "slot": (69, 0),
    "high slot": (50, 0),
    "low slot": (75, 0),
    
    # Corners
    "left corner": (89, 36),
    "right corner": (89, -36),
    
    # Blue line
    "defensive blue line": (25, 0),
    "blue line": (25, 0),
}

NEUTRAL_POSITIONS = {
    "center ice": (0, 0),
    "center": (0, 0),
    "red line": (0, 0),
    "left boards": (0, 42.5),
    "right boards": (0, -42.5),
    "neutral queue left": (10, 38),
    "neutral queue right": (10, -38),
}

def map_position(position: str, zone: str = "offensive") -> Tuple[float, float]:
    """Map natural language position to coordinates."""
    position_lower = position.lower().strip()
    
    if zone == "offensive":
        positions = OFFENSIVE_POSITIONS
    elif zone == "defensive":
        positions = DEFENSIVE_POSITIONS
    else:
        positions = NEUTRAL_POSITIONS
    
    # Direct match
    if position_lower in positions:
        return positions[position_lower]
    
    # Fuzzy match
    for key, coords in positions.items():
        if position_lower in key or key in position_lower:
            return coords
    
    # Default to center of zone
    if zone == "offensive":
        return (-69, 0)  # Offensive zone center
    elif zone == "defensive":
        return (69, 0)   # Defensive zone center
    else:
        return (0, 0)    # Center ice

def calculate_waypoints(from_pos: Tuple[float, float], 
                       to_pos: Tuple[float, float],
                       pattern: str = "direct") -> List[List[float]]:
    """Calculate waypoints for movement patterns.
    Returns array of arrays format: [[x1, y1], [x2, y2], ...]
    """
    
    if pattern == "direct":
        return []
    
    from_x, from_y = from_pos
    to_x, to_y = to_pos
    dx = to_x - from_x
    dy = to_y - from_y
    
    waypoints = []
    
    if pattern == "cross_ice":
        # Cross-ice needs smooth S-curve
        waypoints = [
            [from_x + dx * 0.25, from_y + dy * 0.4],
            [from_x + dx * 0.75, from_y + dy * 0.6]
        ]
        
    elif pattern == "drive":
        # Drive to net - curve around defenders
        waypoints = [
            [from_x + dx * 0.3, from_y + dy * 0.2],
            [to_x - 8, to_y + (5 if dy > 0 else -5)]
        ]
        
    elif pattern == "cycle":
        # Follow boards for cycling
        if abs(from_x) > 80:  # Along end boards
            waypoints = [
                [from_x, from_y + dy * 0.5],
                [from_x + (5 if dx > 0 else -5), to_y]
            ]
        else:  # Along side boards
            waypoints = [
                [from_x + dx * 0.5, from_y],
                [to_x, from_y + dy * 0.3]
            ]
            
    elif pattern == "rush":
        # Rush pattern with speed through neutral zone
        waypoints = [
            [from_x + dx * 0.4, from_y + dy * 0.3]
        ]
        
    elif pattern == "weave":
        # Weaving pattern for agility
        num_weaves = 3
        for i in range(1, num_weaves + 1):
            progress = i / (num_weaves + 1)
            lateral = 8 * (1 if i % 2 == 0 else -1)
            waypoints.append([
                from_x + dx * progress,
                from_y + dy * progress + lateral
            ])
            
    elif pattern == "curve":
        # Simple curve for natural movement
        distance = math.sqrt(dx**2 + dy**2)
        offset = 5 if distance < 30 else 10
        waypoints = [
            [(from_x + to_x) / 2,
             (from_y + to_y) / 2 + offset]
        ]
    
    return waypoints

def parse_relative_position(description: str, reference_positions: Dict[str, Tuple[float, float]] = None) -> Optional[Tuple[float, float]]:
    """Parse relative position descriptions.
    
    Args:
        description: Position description like "5 units left of F1" or "between F1 and F2"
        reference_positions: Dict of existing position names to coordinates
        
    Returns:
        Calculated coordinates or None if not parseable
    """
    if not reference_positions:
        reference_positions = {}
    
    description = description.lower().strip()
    
    # Pattern: "X units [direction] of [reference]"
    units_pattern = r"(\d+(?:\.\d+)?)\s*units?\s*(left|right|above|below|north|south|east|west)\s*(?:of|from)\s*(\w+)"
    match = re.match(units_pattern, description)
    if match:
        distance = float(match.group(1))
        direction = match.group(2)
        reference = match.group(3).upper()
        
        if reference in reference_positions:
            ref_x, ref_y = reference_positions[reference]
            
            # Apply directional offset
            if direction in ["left", "west"]:
                return (ref_x - distance, ref_y)
            elif direction in ["right", "east"]:
                return (ref_x + distance, ref_y)
            elif direction in ["above", "north"]:
                return (ref_x, ref_y + distance)
            elif direction in ["below", "south"]:
                return (ref_x, ref_y - distance)
    
    # Pattern: "between [ref1] and [ref2]"
    between_pattern = r"between\s+(\w+)\s+and\s+(\w+)"
    match = re.search(between_pattern, description)
    if match:
        ref1 = match.group(1).upper()
        ref2 = match.group(2).upper()
        
        if ref1 in reference_positions and ref2 in reference_positions:
            x1, y1 = reference_positions[ref1]
            x2, y2 = reference_positions[ref2]
            return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    # Pattern: "halfway between [ref1] and [ref2]"
    halfway_pattern = r"halfway\s+between\s+(\w+)\s+and\s+(\w+)"
    match = re.search(halfway_pattern, description)
    if match:
        ref1 = match.group(1).upper()
        ref2 = match.group(2).upper()
        
        if ref1 in reference_positions and ref2 in reference_positions:
            x1, y1 = reference_positions[ref1]
            x2, y2 = reference_positions[ref2]
            return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    # Pattern: "[fraction] of the way from [ref1] to [ref2]"
    fraction_pattern = r"(\d+/\d+|half|third|quarter)\s*(?:of\s*the\s*)?way\s+from\s+(\w+)\s+to\s+(\w+)"
    match = re.search(fraction_pattern, description)
    if match:
        fraction_str = match.group(1)
        ref1 = match.group(2).upper()
        ref2 = match.group(3).upper()
        
        # Convert fraction string to float
        if fraction_str == "half":
            fraction = 0.5
        elif fraction_str == "third":
            fraction = 1/3
        elif fraction_str == "quarter":
            fraction = 0.25
        elif "/" in fraction_str:
            parts = fraction_str.split("/")
            fraction = float(parts[0]) / float(parts[1])
        else:
            fraction = 0.5
        
        if ref1 in reference_positions and ref2 in reference_positions:
            x1, y1 = reference_positions[ref1]
            x2, y2 = reference_positions[ref2]
            return (x1 + (x2 - x1) * fraction, y1 + (y2 - y1) * fraction)
    
    # Pattern: "near [reference]" or "close to [reference]"
    near_pattern = r"(?:near|close\s+to|beside|next\s+to)\s+(\w+)"
    match = re.search(near_pattern, description)
    if match:
        reference = match.group(1).upper()
        if reference in reference_positions:
            ref_x, ref_y = reference_positions[reference]
            # Add small random offset (3-5 units)
            import random
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            return (ref_x + offset_x, ref_y + offset_y)
    
    return None

def enhance_position_with_relative(
    position: Union[str, Dict[str, float]], 
    reference_positions: Dict[str, Tuple[float, float]] = None,
    zone: str = "offensive"
) -> Tuple[float, float]:
    """Enhanced position mapping with relative positioning support.
    
    Args:
        position: Either a position string, coordinates dict, or relative description
        reference_positions: Dict of existing position names to coordinates
        zone: Context zone for position mapping
        
    Returns:
        Tuple of (x, y) coordinates
    """
    # Handle dict coordinates
    if isinstance(position, dict):
        return (position.get("x", 0), position.get("y", 0))
    
    # Try relative positioning first
    if reference_positions:
        relative_coords = parse_relative_position(position, reference_positions)
        if relative_coords:
            return relative_coords
    
    # Fall back to standard position mapping
    coords = map_position(position, zone)
    return (coords["x"], coords["y"])