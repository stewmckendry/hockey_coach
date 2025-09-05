"""Zone boundary definitions for hockey rink spatial awareness."""

from typing import Dict, List, Tuple, Optional

def get_zone_boundaries(view: str, zone: str) -> Dict[str, any]:
    """
    Get boundary coordinates for a specific zone/area on the rink.
    
    Args:
        view: Rink view context (offensive, defensive, neutral, full)
        zone: Specific area name (e.g., "slot", "left_circle", "right_point")
    
    Returns:
        Dictionary with boundary information including:
        - min_x, max_x, min_y, max_y: Bounding box
        - center: Center point of the zone
        - description: Human-readable description
    """
    
    # Define boundaries for all zones
    boundaries = {
        "offensive": {
            # Circles
            "left_circle": {
                "min_x": 54, "max_x": 84,
                "min_y": 7.5, "max_y": 37.5,
                "center": {"x": 69, "y": 22.5},
                "description": "Left faceoff circle in offensive zone"
            },
            "right_circle": {
                "min_x": 54, "max_x": 84,
                "min_y": -37.5, "max_y": -7.5,
                "center": {"x": 69, "y": -22.5},
                "description": "Right faceoff circle in offensive zone"
            },
            
            # Slot areas
            "slot": {
                "min_x": 69, "max_x": 86,
                "min_y": -8, "max_y": 8,
                "center": {"x": 77, "y": 0},
                "description": "Prime scoring area in front of net"
            },
            "high_slot": {
                "min_x": 54, "max_x": 69,
                "min_y": -15, "max_y": 15,
                "center": {"x": 61, "y": 0},
                "description": "High slot between circles"
            },
            
            # Points
            "left_point": {
                "min_x": 40, "max_x": 60,
                "min_y": 30, "max_y": 42.5,
                "center": {"x": 54, "y": 38},
                "description": "Left defenseman point position"
            },
            "right_point": {
                "min_x": 40, "max_x": 60,
                "min_y": -42.5, "max_y": -30,
                "center": {"x": 54, "y": -38},
                "description": "Right defenseman point position"
            },
            
            # Corners
            "left_corner": {
                "min_x": 86, "max_x": 100,
                "min_y": 28, "max_y": 42.5,
                "center": {"x": 89, "y": 36},
                "description": "Left corner behind goal line"
            },
            "right_corner": {
                "min_x": 86, "max_x": 100,
                "min_y": -42.5, "max_y": -28,
                "center": {"x": 89, "y": -36},
                "description": "Right corner behind goal line"
            },
            
            # Half walls
            "left_half_wall": {
                "min_x": 69, "max_x": 86,
                "min_y": 30, "max_y": 42.5,
                "center": {"x": 75, "y": 38},
                "description": "Left half wall along boards"
            },
            "right_half_wall": {
                "min_x": 69, "max_x": 86,
                "min_y": -42.5, "max_y": -30,
                "center": {"x": 75, "y": -38},
                "description": "Right half wall along boards"
            },
            
            # Net areas
            "net_front": {
                "min_x": 82, "max_x": 89,
                "min_y": -9, "max_y": 9,
                "center": {"x": 85, "y": 0},
                "description": "Directly in front of the net"
            },
            "behind_net": {
                "min_x": 89, "max_x": 100,
                "min_y": -10, "max_y": 10,
                "center": {"x": 92, "y": 0},
                "description": "Behind the goal line"
            },
            "crease": {
                "min_x": 85, "max_x": 89,
                "min_y": -4, "max_y": 4,
                "center": {"x": 87, "y": 0},
                "description": "Goalie crease area"
            }
        },
        
        "defensive": {
            # Mirror offensive zones with negative x
            "left_circle": {
                "min_x": -84, "max_x": -54,
                "min_y": 7.5, "max_y": 37.5,
                "center": {"x": -69, "y": 22.5},
                "description": "Left faceoff circle in defensive zone"
            },
            "right_circle": {
                "min_x": -84, "max_x": -54,
                "min_y": -37.5, "max_y": -7.5,
                "center": {"x": -69, "y": -22.5},
                "description": "Right faceoff circle in defensive zone"
            },
            "slot": {
                "min_x": -86, "max_x": -69,
                "min_y": -8, "max_y": 8,
                "center": {"x": -77, "y": 0},
                "description": "Defensive zone slot"
            },
            "net_front": {
                "min_x": -89, "max_x": -82,
                "min_y": -9, "max_y": 9,
                "center": {"x": -85, "y": 0},
                "description": "In front of defensive net"
            },
            "left_corner": {
                "min_x": -100, "max_x": -86,
                "min_y": 28, "max_y": 42.5,
                "center": {"x": -89, "y": 36},
                "description": "Left corner in defensive zone"
            },
            "right_corner": {
                "min_x": -100, "max_x": -86,
                "min_y": -42.5, "max_y": -28,
                "center": {"x": -89, "y": -36},
                "description": "Right corner in defensive zone"
            }
        },
        
        "neutral": {
            "center_ice": {
                "min_x": -8, "max_x": 8,
                "min_y": -8, "max_y": 8,
                "center": {"x": 0, "y": 0},
                "description": "Center ice faceoff circle"
            },
            "left_neutral_offensive": {
                "min_x": 15, "max_x": 25,
                "min_y": 17.5, "max_y": 27.5,
                "center": {"x": 20, "y": 22.5},
                "description": "Left neutral dot near offensive zone"
            },
            "right_neutral_offensive": {
                "min_x": 15, "max_x": 25,
                "min_y": -27.5, "max_y": -17.5,
                "center": {"x": 20, "y": -22.5},
                "description": "Right neutral dot near offensive zone"
            },
            "left_neutral_defensive": {
                "min_x": -25, "max_x": -15,
                "min_y": 17.5, "max_y": 27.5,
                "center": {"x": -20, "y": 22.5},
                "description": "Left neutral dot near defensive zone"
            },
            "right_neutral_defensive": {
                "min_x": -25, "max_x": -15,
                "min_y": -27.5, "max_y": -17.5,
                "center": {"x": -20, "y": -22.5},
                "description": "Right neutral dot near defensive zone"
            },
            "left_boards": {
                "min_x": -25, "max_x": 25,
                "min_y": 35, "max_y": 42.5,
                "center": {"x": 0, "y": 38},
                "description": "Along left boards in neutral zone"
            },
            "right_boards": {
                "min_x": -25, "max_x": 25,
                "min_y": -42.5, "max_y": -35,
                "center": {"x": 0, "y": -38},
                "description": "Along right boards in neutral zone"
            }
        }
    }
    
    # Handle view aliases
    if view == "full":
        # For full view, check all zones
        for zone_dict in boundaries.values():
            if zone in zone_dict:
                return zone_dict[zone]
    
    # Get zone-specific boundaries
    if view in boundaries and zone in boundaries[view]:
        return boundaries[view][zone]
    
    # Return generic boundary if not found
    return {
        "min_x": -100, "max_x": 100,
        "min_y": -42.5, "max_y": 42.5,
        "center": {"x": 0, "y": 0},
        "description": f"Unknown zone: {zone} in {view} view",
        "error": "Zone not found - returning full rink boundaries"
    }


def list_available_zones(view: Optional[str] = None) -> Dict[str, List[str]]:
    """
    List all available zones that can be queried.
    
    Args:
        view: Optional view filter (offensive, defensive, neutral)
    
    Returns:
        Dictionary of view names to zone lists
    """
    all_zones = {
        "offensive": [
            "left_circle", "right_circle", "slot", "high_slot",
            "left_point", "right_point", "left_corner", "right_corner",
            "left_half_wall", "right_half_wall", "net_front", 
            "behind_net", "crease"
        ],
        "defensive": [
            "left_circle", "right_circle", "slot", "net_front",
            "left_corner", "right_corner"
        ],
        "neutral": [
            "center_ice", "left_neutral_offensive", "right_neutral_offensive",
            "left_neutral_defensive", "right_neutral_defensive",
            "left_boards", "right_boards"
        ]
    }
    
    if view and view in all_zones:
        return {view: all_zones[view]}
    
    return all_zones