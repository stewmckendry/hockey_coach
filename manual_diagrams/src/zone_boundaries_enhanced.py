"""Enhanced zone boundary definitions with fuzzy matching and suggestions."""

from typing import Dict, List, Tuple, Optional, Any
from difflib import get_close_matches
import re

def get_zone_boundaries_enhanced(view: str, zone: str) -> Dict[str, Any]:
    """
    Enhanced zone boundary function with fuzzy matching and suggestions.
    
    Args:
        view: Rink view context (offensive, defensive, neutral, full)
        zone: Natural language zone description or specific area name
    
    Returns:
        Dictionary with boundary information including:
        - min_x, max_x, min_y, max_y: Bounding box
        - center: Center point of the zone
        - description: Human-readable description
        - suggestions: If zone not found, list of closest matches
        - interpreted_as: What the system interpreted the query as
    """
    
    # Define boundaries for all zones with aliases
    boundaries = {
        "offensive": {
            # Circles and dots
            "left_circle": {
                "min_x": 54, "max_x": 84,
                "min_y": 7.5, "max_y": 37.5,
                "center": {"x": 69, "y": 22.5},
                "description": "Left faceoff circle in offensive zone",
                "aliases": ["left_offensive_circle", "left_offensive_dot", "left_faceoff_dot", "offensive_left_dot"]
            },
            "right_circle": {
                "min_x": 54, "max_x": 84,
                "min_y": -37.5, "max_y": -7.5,
                "center": {"x": 69, "y": -22.5},
                "description": "Right faceoff circle in offensive zone",
                "aliases": ["right_offensive_circle", "right_offensive_dot", "right_faceoff_dot", "offensive_right_dot"]
            },
            
            # Slot areas
            "slot": {
                "min_x": 69, "max_x": 86,
                "min_y": -8, "max_y": 8,
                "center": {"x": 77, "y": 0},
                "description": "Prime scoring area in front of net",
                "aliases": ["scoring_area", "front_of_net", "net_front_offensive"]
            },
            "high_slot": {
                "min_x": 54, "max_x": 69,
                "min_y": -15, "max_y": 15,
                "center": {"x": 61, "y": 0},
                "description": "High slot between circles",
                "aliases": ["between_circles", "middle_offensive"]
            },
            
            # Points - CORRECTED to blue line positions
            "left_point": {
                "min_x": 20, "max_x": 30,
                "min_y": 30, "max_y": 42.5,
                "center": {"x": 25, "y": 38},
                "description": "Left defenseman at blue line",
                "aliases": ["left_d_point", "left_blue_line", "blue_line_left", "left_defense_point"]
            },
            "right_point": {
                "min_x": 20, "max_x": 30,
                "min_y": -42.5, "max_y": -30,
                "center": {"x": 25, "y": -38},
                "description": "Right defenseman at blue line",
                "aliases": ["right_d_point", "right_blue_line", "blue_line_right", "right_defense_point"]
            },
            
            # Half boards (between blue line and goal line)
            "left_half_boards": {
                "min_x": 40, "max_x": 65,
                "min_y": 35, "max_y": 42.5,
                "center": {"x": 52, "y": 38},
                "description": "Left half boards between blue line and goal",
                "aliases": ["left_half_wall", "left_boards_offensive", "half_boards_left"]
            },
            "right_half_boards": {
                "min_x": 40, "max_x": 65,
                "min_y": -42.5, "max_y": -35,
                "center": {"x": 52, "y": -38},
                "description": "Right half boards between blue line and goal",
                "aliases": ["right_half_wall", "right_boards_offensive", "half_boards_right"]
            },
            
            # Corners
            "left_corner": {
                "min_x": 86, "max_x": 100,
                "min_y": 28, "max_y": 42.5,
                "center": {"x": 89, "y": 36},
                "description": "Left corner behind goal line",
                "aliases": ["corner_left", "offensive_left_corner"]
            },
            "right_corner": {
                "min_x": 86, "max_x": 100,
                "min_y": -42.5, "max_y": -28,
                "center": {"x": 89, "y": -36},
                "description": "Right corner behind goal line",
                "aliases": ["corner_right", "offensive_right_corner"]
            },
            
            # Net areas
            "net_front": {
                "min_x": 82, "max_x": 89,
                "min_y": -9, "max_y": 9,
                "center": {"x": 85, "y": 0},
                "description": "Directly in front of the net",
                "aliases": ["in_front", "front_net", "goal_front"]
            },
            "behind_net": {
                "min_x": 89, "max_x": 100,
                "min_y": -10, "max_y": 10,
                "center": {"x": 92, "y": 0},
                "description": "Behind the goal line",
                "aliases": ["behind_goal", "behind_the_net", "gretzky_office"]
            },
            "crease": {
                "min_x": 85, "max_x": 89,
                "min_y": -4, "max_y": 4,
                "center": {"x": 87, "y": 0},
                "description": "Goalie crease area",
                "aliases": ["goalie_crease", "goal_crease"]
            },
            "net": {
                "min_x": 89, "max_x": 89,
                "min_y": -3, "max_y": 3,
                "center": {"x": 89, "y": 0},
                "description": "Goal/net position",
                "aliases": ["goal", "offensive_goal", "offensive_net"]
            }
        },
        
        "defensive": {
            # Circles and dots
            "left_circle": {
                "min_x": -84, "max_x": -54,
                "min_y": 7.5, "max_y": 37.5,
                "center": {"x": -69, "y": 22.5},
                "description": "Left faceoff circle in defensive zone",
                "aliases": ["left_defensive_circle", "left_defensive_dot", "left_defensive_faceoff_dot", "defensive_left_dot"]
            },
            "right_circle": {
                "min_x": -84, "max_x": -54,
                "min_y": -37.5, "max_y": -7.5,
                "center": {"x": -69, "y": -22.5},
                "description": "Right faceoff circle in defensive zone",
                "aliases": ["right_defensive_circle", "right_defensive_dot", "right_defensive_faceoff_dot", "defensive_right_dot"]
            },
            
            # Defensive positions
            "slot": {
                "min_x": -86, "max_x": -69,
                "min_y": -8, "max_y": 8,
                "center": {"x": -77, "y": 0},
                "description": "Defensive zone slot",
                "aliases": ["defensive_slot", "front_defensive_net"]
            },
            "net_front": {
                "min_x": -89, "max_x": -82,
                "min_y": -9, "max_y": 9,
                "center": {"x": -85, "y": 0},
                "description": "In front of defensive net",
                "aliases": ["defensive_net_front", "in_front_defensive"]
            },
            "behind_net": {
                "min_x": -100, "max_x": -89,
                "min_y": -10, "max_y": 10,
                "center": {"x": -92, "y": 0},
                "description": "Behind defensive goal",
                "aliases": ["behind_defensive_net", "defensive_behind_net", "behind_own_net"]
            },
            
            # Defensive corners
            "left_corner": {
                "min_x": -100, "max_x": -86,
                "min_y": 28, "max_y": 42.5,
                "center": {"x": -89, "y": 36},
                "description": "Left corner in defensive zone",
                "aliases": ["defensive_left_corner"]
            },
            "right_corner": {
                "min_x": -100, "max_x": -86,
                "min_y": -42.5, "max_y": -28,
                "center": {"x": -89, "y": -36},
                "description": "Right corner in defensive zone",
                "aliases": ["defensive_right_corner"]
            },
            
            # Defensive boards
            "left_boards": {
                "min_x": -86, "max_x": -25,
                "min_y": 35, "max_y": 42.5,
                "center": {"x": -55, "y": 38},
                "description": "Left boards in defensive zone",
                "aliases": ["defensive_left_boards", "left_wall_defensive"]
            },
            "right_boards": {
                "min_x": -86, "max_x": -25,
                "min_y": -42.5, "max_y": -35,
                "center": {"x": -55, "y": -38},
                "description": "Right boards in defensive zone",
                "aliases": ["defensive_right_boards", "right_wall_defensive"]
            },
            
            # Net position
            "net": {
                "min_x": -89, "max_x": -89,
                "min_y": -3, "max_y": 3,
                "center": {"x": -89, "y": 0},
                "description": "Defensive goal/net position",
                "aliases": ["goal", "defensive_goal", "defensive_net", "own_net"]
            }
        },
        
        "neutral": {
            "center_ice": {
                "min_x": -8, "max_x": 8,
                "min_y": -8, "max_y": 8,
                "center": {"x": 0, "y": 0},
                "description": "Center ice faceoff circle",
                "aliases": ["center", "center_dot", "center_faceoff", "middle_ice"]
            },
            
            # Blue lines
            "offensive_blue_line": {
                "min_x": 24, "max_x": 26,
                "min_y": -42.5, "max_y": 42.5,
                "center": {"x": 25, "y": 0},
                "description": "Offensive blue line",
                "aliases": ["blue_line_offensive", "attacking_blue_line"]
            },
            "defensive_blue_line": {
                "min_x": -26, "max_x": -24,
                "min_y": -42.5, "max_y": 42.5,
                "center": {"x": -25, "y": 0},
                "description": "Defensive blue line",
                "aliases": ["blue_line_defensive", "defending_blue_line", "blue_line", "backing_up_blue_line"]
            },
            
            # Neutral zone dots
            "left_neutral_offensive": {
                "min_x": 15, "max_x": 25,
                "min_y": 17.5, "max_y": 27.5,
                "center": {"x": 20, "y": 22.5},
                "description": "Left neutral dot near offensive zone",
                "aliases": ["left_neutral_dot_offensive"]
            },
            "right_neutral_offensive": {
                "min_x": 15, "max_x": 25,
                "min_y": -27.5, "max_y": -17.5,
                "center": {"x": 20, "y": -22.5},
                "description": "Right neutral dot near offensive zone",
                "aliases": ["right_neutral_dot_offensive"]
            },
            "left_neutral_defensive": {
                "min_x": -25, "max_x": -15,
                "min_y": 17.5, "max_y": 27.5,
                "center": {"x": -20, "y": 22.5},
                "description": "Left neutral dot near defensive zone",
                "aliases": ["left_neutral_dot_defensive"]
            },
            "right_neutral_defensive": {
                "min_x": -25, "max_x": -15,
                "min_y": -27.5, "max_y": -17.5,
                "center": {"x": -20, "y": -22.5},
                "description": "Right neutral dot near defensive zone",
                "aliases": ["right_neutral_dot_defensive"]
            },
            
            # Boards
            "left_boards": {
                "min_x": -25, "max_x": 25,
                "min_y": 35, "max_y": 42.5,
                "center": {"x": 0, "y": 38},
                "description": "Along left boards in neutral zone",
                "aliases": ["neutral_left_boards", "left_wall_neutral", "left_wall", "left_side"]
            },
            "right_boards": {
                "min_x": -25, "max_x": 25,
                "min_y": -42.5, "max_y": -35,
                "center": {"x": 0, "y": -38},
                "description": "Along right boards in neutral zone",
                "aliases": ["neutral_right_boards", "right_wall_neutral", "right_wall", "right_side"]
            }
        }
    }
    
    # Natural language mappings
    nl_mappings = {
        # Blue line variations
        r"blue\s*line": "defensive_blue_line",
        r"backing.*blue": "defensive_blue_line",
        r"retreating.*blue": "defensive_blue_line",
        r"defensive.*blue": "defensive_blue_line",
        r"attacking.*blue": "offensive_blue_line",
        r"offensive.*blue": "offensive_blue_line",
        
        # Faceoff dot variations
        r"left.*defensive.*faceoff": "left_defensive_dot",
        r"right.*defensive.*faceoff": "right_defensive_dot",
        r"left.*offensive.*faceoff": "left_offensive_dot",
        r"right.*offensive.*faceoff": "right_offensive_dot",
        r"center.*faceoff": "center_ice",
        r"center\s*ice": "center_ice",
        
        # Board variations
        r"on.*boards": "left_boards",
        r"along.*boards": "left_boards",
        r"half.*boards": "left_half_boards",
        
        # Behind net variations
        r"behind.*net": "behind_net",
        r"behind.*goal": "behind_net",
        
        # Point variations
        r"at.*point": "left_point",
        r"left.*point": "left_point",
        r"right.*point": "right_point",
        r"blue.*line.*point": "left_point",
    }
    
    # Helper function to find zone
    def find_zone(view_name: str, zone_query: str):
        """Find zone in a specific view."""
        if view_name not in boundaries:
            return None
            
        view_zones = boundaries[view_name]
        
        # Direct match
        if zone_query in view_zones:
            result = view_zones[zone_query].copy()
            result["interpreted_as"] = zone_query
            return result
        
        # Check aliases
        for zone_name, zone_data in view_zones.items():
            if "aliases" in zone_data:
                if zone_query in zone_data["aliases"]:
                    result = zone_data.copy()
                    result["interpreted_as"] = f"{zone_query} (alias for {zone_name})"
                    return result
        
        return None
    
    # Clean up the zone query
    zone_lower = zone.lower().strip()
    zone_clean = re.sub(r'[_-]', ' ', zone_lower)
    
    # Try natural language patterns first
    for pattern, mapped_zone in nl_mappings.items():
        if re.search(pattern, zone_clean):
            # Try to find in the specified view
            result = find_zone(view, mapped_zone)
            if not result and view == "full":
                # Try all views for full
                for v in ["offensive", "defensive", "neutral"]:
                    result = find_zone(v, mapped_zone)
                    if result:
                        break
            if result:
                result["interpreted_as"] = f"'{zone}' interpreted as {mapped_zone}"
                return result
    
    # Try exact match or alias
    result = find_zone(view, zone_lower)
    if result:
        return result
    
    # For full view, check all zones
    if view == "full":
        for view_name in ["offensive", "defensive", "neutral"]:
            result = find_zone(view_name, zone_lower)
            if result:
                return result
    
    # Fuzzy matching - collect all possible zone names
    all_zone_names = []
    zones_to_check = boundaries.values() if view == "full" else [boundaries.get(view, {})]
    
    for zone_dict in zones_to_check:
        for zone_name, zone_data in zone_dict.items():
            all_zone_names.append(zone_name)
            if "aliases" in zone_data:
                all_zone_names.extend(zone_data["aliases"])
    
    # Find close matches
    close_matches = get_close_matches(zone_lower, all_zone_names, n=5, cutoff=0.6)
    
    # If we have close matches, suggest them
    if close_matches:
        # Try the best match
        best_match = close_matches[0]
        for view_name in (boundaries.keys() if view == "full" else [view]):
            if view_name in boundaries:
                result = find_zone(view_name, best_match)
                if result:
                    result["warning"] = f"Zone '{zone}' not found. Using closest match: '{best_match}'"
                    result["suggestions"] = close_matches[1:] if len(close_matches) > 1 else []
                    result["interpreted_as"] = f"'{zone}' matched to '{best_match}' (fuzzy match)"
                    return result
    
    # Return error with suggestions
    return {
        "min_x": -100, "max_x": 100,
        "min_y": -42.5, "max_y": 42.5,
        "center": {"x": 0, "y": 0},
        "description": f"Zone '{zone}' not found in {view} view",
        "error": "Zone not found - returning full rink boundaries",
        "suggestions": close_matches[:3] if close_matches else [
            "Try: center_ice, left_circle, right_circle, slot, behind_net",
            "Use 'defensive_' or 'offensive_' prefix for zone-specific areas",
            "Common: blue_line, half_boards, point, corner"
        ],
        "interpreted_as": f"Failed to interpret '{zone}'",
        "available_zones": list_zones_for_view(view)
    }


def list_zones_for_view(view: str) -> List[str]:
    """List available zones for a specific view."""
    boundaries = {
        "offensive": [
            "left_circle", "right_circle", "slot", "high_slot",
            "left_point", "right_point", "left_corner", "right_corner",
            "left_half_boards", "right_half_boards", "net_front", 
            "behind_net", "crease", "net"
        ],
        "defensive": [
            "left_circle", "right_circle", "slot", "net_front",
            "left_corner", "right_corner", "behind_net",
            "left_boards", "right_boards", "net"
        ],
        "neutral": [
            "center_ice", "offensive_blue_line", "defensive_blue_line",
            "left_neutral_offensive", "right_neutral_offensive",
            "left_neutral_defensive", "right_neutral_defensive",
            "left_boards", "right_boards"
        ]
    }
    
    if view == "full":
        all_zones = []
        for zones in boundaries.values():
            all_zones.extend(zones)
        return all_zones
    
    return boundaries.get(view, [])