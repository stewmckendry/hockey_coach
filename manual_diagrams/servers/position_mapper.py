"""
Position mapping utilities for hockey diagrams.
Converts natural language positions to coordinates.
Coordinate system: x: -100 to 100 (left to right), y: -42.5 to 42.5 (bottom to top)
"""

from typing import Dict, Any, Optional, List, Tuple, Union
import math
import re

# Position mappings by zone
# OFFENSIVE ZONE IS RIGHT SIDE (positive x values)
OFFENSIVE_POSITIONS = {
    # Faceoff dots and circle positions
    "left faceoff dot": (69, 22.5),
    "right faceoff dot": (69, -22.5),
    "left dot": (69, 22.5),
    "right dot": (69, -22.5),
    
    # Offensive zone faceoff positions - HOME TEAM (attacking from left side of dot)
    # LEFT DOT: Left wing outside, Right wing at hashmark on circle edge
    "offensive left faceoff home center": (67, 22.5),  # LEFT side of dot (home attacks)
    "offensive left faceoff home left wing": (67, 37),  # Left wing outside circle
    "offensive left faceoff home right wing": (67, 7.5),  # Right wing at hashmark on circle edge
    "offensive left faceoff home left defense": (45, 30),  # Left D back support
    "offensive left faceoff home right defense": (45, 15),  # Right D back support
    
    # RIGHT DOT: Right wing outside, Left wing at hashmark on circle edge
    "offensive right faceoff home center": (67, -22.5),  # LEFT side of dot
    "offensive right faceoff home right wing": (67, -37),  # Right wing outside circle
    "offensive right faceoff home left wing": (67, -7.5),  # Left wing at hashmark on circle edge
    "offensive right faceoff home left defense": (45, -15),  # Left D back support
    "offensive right faceoff home right defense": (45, -30),  # Right D back support
    
    # Offensive zone faceoff positions - AWAY TEAM (defending from right side of dot)
    # LEFT DOT: Away team faces opposite direction, so their right wing is outside
    "offensive left faceoff away center": (71, 22.5),  # RIGHT side of dot (away defends)
    "offensive left faceoff away right wing": (71, 37),  # Right wing outside (their perspective)
    "offensive left faceoff away left wing": (71, 7.5),  # Left wing at hashmark (their perspective)
    "offensive left faceoff away right defense": (84, 30),  # Right D protecting net
    "offensive left faceoff away left defense": (84, 15),  # Left D protecting net
    
    # RIGHT DOT: Away team faces opposite direction, so their left wing is outside
    "offensive right faceoff away center": (71, -22.5),  # RIGHT side of dot
    "offensive right faceoff away left wing": (71, -37),  # Left wing outside (their perspective)
    "offensive right faceoff away right wing": (71, -7.5),  # Right wing at hashmark (their perspective)
    "offensive right faceoff away left defense": (84, -15),  # Left D protecting net
    "offensive right faceoff away right defense": (84, -30),  # Right D protecting net
    
    # Net area
    "behind net": (89, 0),
    "behind the net": (89, 0),
    "net front": (83, 0),
    "in front of net": (83, 0),
    "crease": (86, 0),
    "goalie": (86, 0),  # In the crease, just below goal line
    "left post": (89, 6),
    "right post": (89, -6),
    
    # Slot area - Low (midpoint between hashmarks and goal line)
    # Hashmarks at x=69, goal line at x=89, midpoint = 79
    "low slot": (79, 0),
    "low slot middle": (79, 0),
    "low slot left": (79, 20),  # Halfway to boards
    "low slot right": (79, -20),  # Halfway to boards
    
    # Slot area - Mid (at circle hashmarks)
    # Circle hashmarks at x=69
    "mid slot": (69, 0),
    "mid slot middle": (69, 0),
    "mid slot left": (69, 20),  # Halfway to boards
    "mid slot right": (69, -20),  # Halfway to boards
    
    # Slot area - High (midpoint between circle hashmarks and blue line)
    # Circle hashmarks at x=69, blue line at x=25, midpoint = 47
    "high slot": (47, 0),
    "high slot middle": (47, 0),
    "high slot left": (47, 20),  # Halfway to boards
    "high slot right": (47, -20),  # Halfway to boards
    "slot": (69, 0),  # Default to mid slot
    
    # Hash marks
    "left hash": (75, 22.5),
    "right hash": (75, -22.5),
    "left hash marks": (75, 22.5),
    "right hash marks": (75, -22.5),
    
    # Corners
    "left corner": (89, 36),
    "right corner": (89, -36),
    
    # Half wall
    "left half wall": (69, 38),
    "right half wall": (69, -38),
    "half wall": (69, 38),  # Default to left
    
    # Blue line/points (inside blue line, not on it)
    "point middle": (30, 0),
    "point": (30, 0),  # Default to middle
    "point left": (30, 20),
    "point right": (30, -20),
    "point left boards": (30, 38),  # Near boards to stop puck
    "point right boards": (30, -38),  # Near boards to stop puck
    "blue line": (25, 0),
    "offensive blue line": (25, 0),
    
    # Goal line
    "goal line": (89, 0),
    "goal line extended": (89, 38),
    
    # Queue positions (off ice for visibility)
    "left queue": (20, -38),
    "right queue": (20, 38),
    "corner queue left": (75, -38),
    "corner queue right": (75, 38),
}

DEFENSIVE_POSITIONS = {
    # Faceoff dots
    "left faceoff dot": (-69, 22.5),
    "right faceoff dot": (-69, -22.5),
    "left dot": (-69, 22.5),
    "right dot": (-69, -22.5),
    
    # Defensive zone faceoff positions - HOME TEAM (defending, faces toward own net)
    # LEFT DOT: Home team defends, so their right wing is outside (flipped orientation)
    "defensive left faceoff home center": (-71, 22.5),  # RIGHT side of dot (home defends)
    "defensive left faceoff home right wing": (-71, 37),  # Right wing outside (defender perspective)
    "defensive left faceoff home left wing": (-71, 7.5),  # Left wing at hashmark (defender perspective)
    "defensive left faceoff home right defense": (-84, 30),  # Right D protecting net
    "defensive left faceoff home left defense": (-84, 15),  # Left D protecting net
    
    # RIGHT DOT: Home team defends, so their left wing is outside (flipped orientation)
    "defensive right faceoff home center": (-71, -22.5),  # RIGHT side of dot
    "defensive right faceoff home left wing": (-71, -37),  # Left wing outside (defender perspective)
    "defensive right faceoff home right wing": (-71, -7.5),  # Right wing at hashmark (defender perspective)
    "defensive right faceoff home left defense": (-84, -15),  # Left D protecting net
    "defensive right faceoff home right defense": (-84, -30),  # Right D protecting net
    
    # Defensive zone faceoff positions - AWAY TEAM (attacking from left side of dot)
    # LEFT DOT: Away team attacks, left wing outside, right wing at hashmark
    "defensive left faceoff away center": (-67, 22.5),  # LEFT side of dot (away attacks)
    "defensive left faceoff away left wing": (-67, 37),  # Left wing outside circle
    "defensive left faceoff away right wing": (-67, 7.5),  # Right wing at hashmark on circle edge
    "defensive left faceoff away left defense": (-45, 30),  # Left D back support
    "defensive left faceoff away right defense": (-45, 15),  # Right D back support
    
    # RIGHT DOT: Away team attacks, right wing outside, left wing at hashmark
    "defensive right faceoff away center": (-67, -22.5),  # LEFT side of dot
    "defensive right faceoff away right wing": (-67, -37),  # Right wing outside circle
    "defensive right faceoff away left wing": (-67, -7.5),  # Left wing at hashmark on circle edge
    "defensive right faceoff away left defense": (-45, -15),  # Left D back support
    "defensive right faceoff away right defense": (-45, -30),  # Right D back support
    
    # Net area
    "behind net": (-89, 0),
    "behind the net": (-89, 0),
    "net front": (-83, 0),
    "in front of net": (-83, 0),
    "crease": (-86, 0),
    "goalie": (-86, 0),  # In the crease, just below goal line
    "left post": (-89, 6),
    "right post": (-89, -6),
    
    # Slot area - Low (midpoint between hashmarks and goal line)
    # Hashmarks at x=-69, goal line at x=-89, midpoint = -79
    "low slot": (-79, 0),
    "low slot middle": (-79, 0),
    "low slot left": (-79, 20),  # Halfway to boards
    "low slot right": (-79, -20),  # Halfway to boards
    
    # Slot area - Mid (at circle hashmarks)
    # Circle hashmarks at x=-69
    "mid slot": (-69, 0),
    "mid slot middle": (-69, 0),
    "mid slot left": (-69, 20),  # Halfway to boards
    "mid slot right": (-69, -20),  # Halfway to boards
    
    # Slot area - High (midpoint between circle hashmarks and blue line)
    # Circle hashmarks at x=-69, blue line at x=-25, midpoint = -47
    "high slot": (-47, 0),
    "high slot middle": (-47, 0),
    "high slot left": (-47, 20),  # Halfway to boards
    "high slot right": (-47, -20),  # Halfway to boards
    "slot": (-69, 0),  # Default to mid slot
    
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
    
    # Blue line/points (inside blue line, not on it)
    "point middle": (-30, 0),
    "point": (-30, 0),  # Default to middle
    "point left": (-30, 20),
    "point right": (-30, -20),
    "point left boards": (-30, 38),  # Near boards to stop puck
    "point right boards": (-30, -38),  # Near boards to stop puck
    "defensive blue line": (-25, 0),
    "blue line": (-25, 0),
}

NEUTRAL_POSITIONS = {
    # ==========================================
    # CENTER ICE POSITIONS (keep only 2 aliases)
    # ==========================================
    "center ice": (0, 0),
    "center faceoff": (0, 0),
    
    # Center ice face-off positions - HOME TEAM (increased right offset)
    "center faceoff home center": (3, 0),  # Further RIGHT for home team attacking right
    "center faceoff home right wing": (4, -14),  # Outside circle, more right
    "center faceoff home left wing": (4, 14),   # Outside circle, more right
    "center faceoff home right defense": (12, -8),  # On circle edge, more right
    "center faceoff home left defense": (12, 8),    # On circle edge, more right
    
    # Center ice face-off positions - AWAY TEAM (increased left offset)
    "center faceoff away center": (-3, 0),  # Further LEFT for away team
    "center faceoff away right wing": (-4, -14),  # Outside circle, more left
    "center faceoff away left wing": (-4, 14),   # Outside circle, more left
    "center faceoff away right defense": (-12, -8),  # On circle edge, more left
    "center faceoff away left defense": (-12, 8),    # On circle edge, more left
    
    # ==========================================
    # OFFSIDE DOTS - NEAR DEFENSIVE ZONE (left side)
    # ==========================================
    "offside dot defensive left": (-20, 22.5),   # Left side, near defensive zone
    "offside dot defensive right": (-20, -22.5),  # Right side, near defensive zone
    
    # Face-off positions at defensive zone offside dots - HOME TEAM (attacking right)
    "offside defensive left faceoff home center": (-17, 22.5),  # Right side of dot
    "offside defensive left faceoff home wing outside": (-17, 34),  # Near boards, aligned with center
    "offside defensive left faceoff home wing inside": (-17, 16),  # Inside, aligned with center
    "offside defensive left faceoff home defense left": (-10, 34),  # Back, aligned with outside wing
    "offside defensive left faceoff home defense right": (-10, 16),  # Back, aligned with inside wing
    
    "offside defensive right faceoff home center": (-17, -22.5),  # Right side of dot
    "offside defensive right faceoff home wing outside": (-17, -34),  # Near boards, aligned
    "offside defensive right faceoff home wing inside": (-17, -16),  # Inside, aligned
    "offside defensive right faceoff home defense left": (-10, -16),  # Back, aligned with inside wing
    "offside defensive right faceoff home defense right": (-10, -34),  # Back, aligned with outside wing
    
    # Face-off positions at defensive zone offside dots - AWAY TEAM (defending)
    "offside defensive left faceoff away center": (-23, 22.5),  # Left side of dot
    "offside defensive left faceoff away wing outside": (-23, 34),  # Aligned with home wing
    "offside defensive left faceoff away wing inside": (-23, 16),  # Aligned with home wing
    "offside defensive left faceoff away defense left": (-30, 34),  # Back, aligned with wings
    "offside defensive left faceoff away defense right": (-30, 16),  # Back, aligned with wings
    
    "offside defensive right faceoff away center": (-23, -22.5),  # Left side of dot
    "offside defensive right faceoff away wing outside": (-23, -34),  # Aligned
    "offside defensive right faceoff away wing inside": (-23, -16),  # Aligned
    "offside defensive right faceoff away defense left": (-30, -16),  # Back, aligned
    "offside defensive right faceoff away defense right": (-30, -34),  # Back, aligned
    
    # ==========================================
    # OFFSIDE DOTS - NEAR OFFENSIVE ZONE (right side)
    # ==========================================
    "offside dot offensive left": (20, 22.5),   # Left side, near offensive zone
    "offside dot offensive right": (20, -22.5),  # Right side, near offensive zone
    
    # Face-off positions at offensive zone offside dots - HOME TEAM (attacking right)
    "offside offensive left faceoff home center": (23, 22.5),  # Right side of dot
    "offside offensive left faceoff home wing outside": (23, 34),  # Near boards, aligned
    "offside offensive left faceoff home wing inside": (23, 16),  # Inside, aligned
    "offside offensive left faceoff home defense left": (30, 34),  # Back, aligned with outside wing
    "offside offensive left faceoff home defense right": (30, 16),  # Back, aligned with inside wing
    
    "offside offensive right faceoff home center": (23, -22.5),  # Right side of dot
    "offside offensive right faceoff home wing outside": (23, -34),  # Near boards, aligned
    "offside offensive right faceoff home wing inside": (23, -16),  # Inside, aligned
    "offside offensive right faceoff home defense left": (30, -16),  # Back, aligned with inside wing
    "offside offensive right faceoff home defense right": (30, -34),  # Back, aligned with outside wing
    
    # Face-off positions at offensive zone offside dots - AWAY TEAM (defending)
    "offside offensive left faceoff away center": (17, 22.5),  # Left side of dot
    "offside offensive left faceoff away wing outside": (17, 34),  # Aligned with home wing
    "offside offensive left faceoff away wing inside": (17, 16),  # Aligned with home wing
    "offside offensive left faceoff away defense left": (10, 34),  # Back, aligned with wings
    "offside offensive left faceoff away defense right": (10, 16),  # Back, aligned with wings
    
    "offside offensive right faceoff away center": (17, -22.5),  # Left side of dot
    "offside offensive right faceoff away wing outside": (17, -34),  # Aligned
    "offside offensive right faceoff away wing inside": (17, -16),  # Aligned
    "offside offensive right faceoff away defense left": (10, -16),  # Back, aligned
    "offside offensive right faceoff away defense right": (10, -34),  # Back, aligned
    
    # ==========================================
    # BOARD AND WALL POSITIONS
    # ==========================================
    "left boards": (0, 42.5),
    "right boards": (0, -42.5),
    "neutral zone left wall": (12, 38),   # Along boards in neutral zone
    "neutral zone right wall": (12, -38),
    
    # ==========================================
    # BLUE LINE REFERENCES (for neutral zone context)
    # ==========================================
    "defensive blue line center": (-25, 0),  # Left side blue line
    "offensive blue line center": (25, 0),   # Right side blue line
    
    # ==========================================
    # BLUE LINE/BOARDS DRILL QUEUE POSITIONS
    # ==========================================
    # Defensive blue line queues (left side, x=-25)
    "defensive blue line left boards queue": (-25, 39),  # Near boards, offset inside
    "defensive blue line right boards queue": (-25, -39),  # Near boards, offset inside
    "defensive blue line left queue 2": (-30, 39),  # Second in line
    "defensive blue line left queue 3": (-35, 39),  # Third in line
    "defensive blue line right queue 2": (-30, -39),  # Second in line
    "defensive blue line right queue 3": (-35, -39),  # Third in line
    
    # Offensive blue line queues (right side, x=25)
    "offensive blue line left boards queue": (25, 39),  # Near boards, offset inside
    "offensive blue line right boards queue": (25, -39),  # Near boards, offset inside
    "offensive blue line left queue 2": (30, 39),  # Second in line
    "offensive blue line left queue 3": (35, 39),  # Third in line
    "offensive blue line right queue 2": (30, -39),  # Second in line
    "offensive blue line right queue 3": (35, -39),  # Third in line
    
    # ==========================================
    # BENCH/QUEUE POSITIONS (renamed for clarity)
    # ==========================================
    "home bench left side": (10, 38),   # Home team bench area
    "home bench right side": (10, -38),
    "away bench left side": (-10, 38),  # Away team bench area
    "away bench right side": (-10, -38),
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
    
    # Hockey-specific patterns
    elif pattern == "rim":
        # Rim along boards behind net (for puck movement)
        # This is typically in same zone, going around behind net
        waypoints = [
            [from_x, 38 * (1 if from_y > 0 else -1)],  # To boards
            [89 * (1 if from_x > 0 else -1), 38 * (1 if from_y > 0 else -1)],  # Along boards to corner
            [89 * (1 if from_x > 0 else -1), 0],  # Behind net
            [89 * (1 if from_x > 0 else -1), 38 * (1 if to_y > 0 else -1)],  # To other corner
            [to_x, to_y]  # Final position
        ]
        
    elif pattern == "dump":
        # Dump in from neutral zone - high and deep
        waypoints = [
            [from_x + dx * 0.3, from_y + dy * 0.2],  # Initial trajectory
            [85 * (1 if to_x > 0 else -1), 35 * (1 if to_y > 0 else -1)]  # High into corner
        ]
        
    elif pattern == "chip":
        # Quick chip past defender
        waypoints = [
            [from_x + dx * 0.4, from_y + dy * 0.3 + 5]  # Small arc over/around
        ]
        
    elif pattern == "sauce":
        # Sauce pass with elevation arc
        mid_x = (from_x + to_x) / 2
        mid_y = (from_y + to_y) / 2
        # Add height to trajectory
        waypoints = [
            [mid_x, mid_y + 8]  # Arc over obstacles
        ]
        
    elif pattern == "wrap":
        # Wrap around behind net (usually from behind net to front)
        if abs(from_x) > 85:  # Starting behind net
            # Go around to front
            waypoints = [
                [89 * (1 if from_x > 0 else -1), 15 * (1 if to_y > 0 else -1)],  # Start wrap
                [85 * (1 if from_x > 0 else -1), to_y],  # Come around
            ]
        else:
            # General wrap pattern
            net_x = 89 * (1 if from_x > 50 or to_x > 50 else -1)
            waypoints = [
                [net_x, from_y * 0.5],  # Approach net
                [net_x, 0],  # Behind net
                [net_x, to_y * 0.5],  # Come out other side
            ]
        
    elif pattern == "bank":
        # Bank pass off boards
        board_y = 40 * (1 if abs(from_y) > abs(to_y) else -1)
        waypoints = [
            [(from_x + to_x) / 2, board_y]  # Hit boards midway
        ]
        
    elif pattern == "stretch":
        # Long stretch pass through zones
        # Add slight arc for realism
        waypoints = [
            [from_x + dx * 0.5, from_y + dy * 0.5 + 3]
        ]
        
    elif pattern == "button_hook":
        # Curl back to maintain possession
        curl_back = 12
        waypoints = [
            [from_x + dx * 0.3, from_y],  # Forward
            [from_x + dx * 0.3 - curl_back, from_y - 8],  # Start curl
            [from_x - curl_back, from_y],  # Complete curl
            [to_x, to_y]  # Continue to destination
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