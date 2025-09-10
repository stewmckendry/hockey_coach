"""
Zone-specific offset system for hockey diagram positioning.

This module defines contextually appropriate offset descriptions for each zone type,
ensuring LLMs only use relevant positioning terms for each area of the rink.
"""

from typing import Dict, List

# Zone-specific offset descriptions
ZONE_OFFSET_MAP: Dict[str, List[str]] = {
    # DEFENSIVE CORNER ZONES
    "d-corner-left-high": ["center", "boards-side", "circle-side", "goal-line-side", "blue-line-side"],
    "d-corner-right-high": ["center", "boards-side", "circle-side", "goal-line-side", "blue-line-side"],
    "d-corner-left-low": ["center", "boards-side", "circle-side", "goal-line-side", "net-side"],
    "d-corner-right-low": ["center", "boards-side", "circle-side", "goal-line-side", "net-side"],
    
    # DEFENSIVE CIRCLE ZONES  
    "d-circle-left-high": ["center", "circle-edge", "between-circles", "hash-marks", "top-of-circle"],
    "d-circle-right-high": ["center", "circle-edge", "between-circles", "hash-marks", "top-of-circle"],
    "d-circle-left-center": ["center", "circle-edge", "face-off-dot", "hash-marks", "goal-line"],
    "d-circle-right-center": ["center", "circle-edge", "face-off-dot", "hash-marks", "goal-line"],
    "d-circle-left-low": ["center", "circle-edge", "face-off-dot", "hash-marks", "crease-side"],
    "d-circle-right-low": ["center", "circle-edge", "face-off-dot", "hash-marks", "crease-side"],
    "d-circle-left-boards": ["center", "boards-side", "circle-edge", "below-goal-line"],
    "d-circle-right-boards": ["center", "boards-side", "circle-edge", "below-goal-line"],
    
    # DEFENSIVE BEHIND NET ZONES
    "d-behind-net-left": ["center", "tight-to-net", "corner-side", "boards-side", "goal-line"],
    "d-behind-net-right": ["center", "tight-to-net", "corner-side", "boards-side", "goal-line"],
    
    # NEUTRAL ZONES
    "neutral-left-wing-high": ["center", "boards-side", "blue-line-side", "center-ice-side"],
    "neutral-right-wing-high": ["center", "boards-side", "blue-line-side", "center-ice-side"],
    "neutral-left-center-high": ["center", "center-line-side", "blue-line-side", "face-off-dot"],
    "neutral-right-center-high": ["center", "center-line-side", "blue-line-side", "face-off-dot"],
    "neutral-left-center-low": ["center", "center-line-side", "blue-line-side", "face-off-dot"],
    "neutral-right-center-low": ["center", "center-line-side", "blue-line-side", "face-off-dot"],
    "neutral-left-wing-low": ["center", "boards-side", "blue-line-side", "center-ice-side"],
    "neutral-right-wing-low": ["center", "boards-side", "blue-line-side", "center-ice-side"],
    
    # OFFENSIVE CORNER ZONES
    "o-corner-left-high": ["center", "boards-side", "circle-side", "blue-line-side", "goal-line-side"],
    "o-corner-right-high": ["center", "boards-side", "circle-side", "blue-line-side", "goal-line-side"],
    "o-corner-left-low": ["center", "boards-side", "circle-side", "net-side", "goal-line-side"],
    "o-corner-right-low": ["center", "boards-side", "circle-side", "net-side", "goal-line-side"],
    
    # OFFENSIVE POINT/SLOT ZONES
    "o-point-left": ["center", "blue-line", "hash-marks", "circle-edge", "slot-side"],
    "o-point-right": ["center", "blue-line", "hash-marks", "circle-edge", "slot-side"],
    "o-point-center-left": ["center", "between-points", "hash-marks", "slot-side", "blue-line"],
    "o-point-center-right": ["center", "between-points", "hash-marks", "slot-side", "blue-line"],
    "o-high-slot-high": ["center", "slot-edge", "between-circles", "top-of-slot", "point-side"],
    "o-slot-high": ["center", "slot-center", "between-circles", "net-front", "point-side"],
    "o-slot-low": ["center", "slot-center", "between-circles", "net-front", "crease-side"],
    "o-low-slot": ["center", "slot-edge", "between-circles", "crease-front", "goal-mouth"],
    
    # OFFENSIVE BEHIND NET ZONES
    "o-behind-net-left": ["center", "tight-to-net", "corner-side", "boards-side", "goal-line"],
    "o-behind-net-right": ["center", "tight-to-net", "corner-side", "boards-side", "goal-line"],
}

# Universal offset that works in any zone
UNIVERSAL_OFFSETS = ["center"]

# Validation function
def get_valid_offsets(zone_name: str) -> List[str]:
    """
    Get valid offset descriptions for a specific zone.
    
    Args:
        zone_name: Name of the zone (e.g., "o-slot-high")
        
    Returns:
        List of valid offset descriptions for that zone
    """
    return ZONE_OFFSET_MAP.get(zone_name, ["center"])

def validate_offset(zone_name: str, offset_description: str) -> bool:
    """
    Validate if an offset description is appropriate for a zone.
    
    Args:
        zone_name: Name of the zone
        offset_description: Proposed offset description
        
    Returns:
        True if valid, False otherwise
    """
    valid_offsets = get_valid_offsets(zone_name)
    return offset_description in valid_offsets

# Offset descriptions with explanations
OFFSET_EXPLANATIONS = {
    # Universal
    "center": "Center of the zone",
    
    # Positional relationships
    "boards-side": "Closer to the side boards",
    "center-ice-side": "Closer to center ice", 
    "circle-side": "Closer to face-off circle",
    "circle-edge": "At the edge of face-off circle",
    "between-circles": "Between the two face-off circles",
    "face-off-dot": "Near the face-off dot",
    "hash-marks": "At the hash marks",
    
    # Goal-relative positions
    "net-front": "In front of the net",
    "net-side": "Closer to the net",
    "tight-to-net": "Very close to the net",
    "crease-side": "Closer to the goal crease",
    "crease-front": "In front of the goal crease",
    "goal-mouth": "At the goal mouth",
    "goal-line": "At or near the goal line",
    "goal-line-side": "Closer to the goal line",
    
    # Line-relative positions
    "blue-line": "At or near the blue line",
    "blue-line-side": "Closer to the blue line",
    "center-line-side": "Closer to center line",
    "below-goal-line": "Below the goal line",
    
    # Zone-specific positions
    "slot-center": "Center of the offensive slot",
    "slot-edge": "Edge of the offensive slot", 
    "slot-side": "Closer to the offensive slot",
    "top-of-slot": "Top of the offensive slot",
    "point-side": "Closer to the point position",
    "between-points": "Between the point positions",
    "top-of-circle": "Top of the face-off circle",
    "corner-side": "Closer to the corner"
}

def print_zone_offset_guide():
    """Print a comprehensive guide of zones and their valid offsets."""
    print("ZONE-SPECIFIC OFFSET GUIDE")
    print("=" * 50)
    
    zone_groups = {
        "DEFENSIVE CORNER ZONES": [
            "d-corner-left-high", "d-corner-right-high", 
            "d-corner-left-low", "d-corner-right-low"
        ],
        "DEFENSIVE CIRCLE ZONES": [
            "d-circle-left-high", "d-circle-right-high",
            "d-circle-left-center", "d-circle-right-center",
            "d-circle-left-low", "d-circle-right-low",
            "d-circle-left-boards", "d-circle-right-boards"
        ],
        "DEFENSIVE BEHIND NET": [
            "d-behind-net-left", "d-behind-net-right"
        ],
        "NEUTRAL ZONES": [
            "neutral-left-wing-high", "neutral-right-wing-high",
            "neutral-left-center-high", "neutral-right-center-high",
            "neutral-left-center-low", "neutral-right-center-low",
            "neutral-left-wing-low", "neutral-right-wing-low"
        ],
        "OFFENSIVE CORNER ZONES": [
            "o-corner-left-high", "o-corner-right-high",
            "o-corner-left-low", "o-corner-right-low"
        ],
        "OFFENSIVE POINT/SLOT ZONES": [
            "o-point-left", "o-point-right",
            "o-point-center-left", "o-point-center-right",
            "o-high-slot-high", "o-slot-high", 
            "o-slot-low", "o-low-slot"
        ],
        "OFFENSIVE BEHIND NET": [
            "o-behind-net-left", "o-behind-net-right"
        ]
    }
    
    for group_name, zones in zone_groups.items():
        print(f"\n{group_name}")
        print("-" * len(group_name))
        for zone in zones:
            offsets = get_valid_offsets(zone)
            print(f"{zone:25} → {', '.join(offsets)}")

if __name__ == "__main__":
    print_zone_offset_guide()