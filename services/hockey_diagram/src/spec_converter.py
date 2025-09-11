"""
Spec Converter - Convert between dict and DiagramSpec objects.
Handles missing fields gracefully for robust MCP tool operation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

# Import or define the actual classes
try:
    from hockey_diagram_builder import DiagramSpec, Player, Movement, Zone, Annotation, Equipment
except ImportError:
    # Fallback definitions if imports fail
    @dataclass
    class Player:
        type: str
        position: str
        coordinates: Dict[str, float]
        team: str = "home"
        has_puck: bool = False
        label: str = ""
    
    @dataclass
    class Movement:
        type: str
        from_pos: Dict[str, float]
        to_pos: Dict[str, float]
        style: str = "solid"
        label: str = ""
        waypoints: Optional[List] = None
    
    @dataclass
    class Zone:
        type: str
        shape: str
        bounds: Dict[str, Any]
        team: str = "neutral"
        opacity: float = 0.3
        color: str = "blue"
        label: str = ""
    
    @dataclass
    class Annotation:
        text: str
        position: Optional[Dict[str, float]] = None
    
    @dataclass
    class DiagramSpec:
        title: str
        rink: Dict[str, str]
        players: List[Player]
        movements: List[Movement]
        zones: List[Zone]
        annotations: List[str]
        metadata: Dict[str, Any] = field(default_factory=dict)


def dict_to_player(player_dict: Dict[str, Any]) -> Optional[Player]:
    """Convert dict to Player object with error handling."""
    try:
        # Required fields
        required = ["type", "position", "coordinates"]
        if not all(k in player_dict for k in required):
            logger.warning(f"Player missing required fields: {player_dict}")
            return None
        
        # Convert coordinates from dict to tuple if needed
        coordinates = player_dict["coordinates"]
        if isinstance(coordinates, dict):
            coordinates = (coordinates["x"], coordinates["y"])
        
        return Player(
            type=player_dict["type"],
            position=player_dict["position"],
            coordinates=coordinates,
            team=player_dict.get("team", "home"),
            has_puck=player_dict.get("has_puck", False),
            label=player_dict.get("label", "")
        )
    except Exception as e:
        logger.error(f"Failed to convert player: {e}")
        return None


def dict_to_movement(movement_dict: Dict[str, Any]) -> Optional[Movement]:
    """Convert dict to Movement object with error handling."""
    try:
        # Required fields
        required = ["type", "from_pos", "to_pos"]
        if not all(k in movement_dict for k in required):
            logger.warning(f"Movement missing required fields: {movement_dict}")
            return None
        
        # Convert positions from dict format to tuple format
        from_pos = movement_dict["from_pos"]
        if isinstance(from_pos, dict):
            from_pos = (from_pos["x"], from_pos["y"])
        
        to_pos = movement_dict["to_pos"]
        if isinstance(to_pos, dict):
            to_pos = (to_pos["x"], to_pos["y"])
        
        # Convert waypoints from dict format to tuple format if present
        waypoints = None
        if "waypoints" in movement_dict and movement_dict["waypoints"]:
            waypoints = []
            for wp in movement_dict["waypoints"]:
                if isinstance(wp, dict):
                    waypoints.append((wp["x"], wp["y"]))
                elif isinstance(wp, (list, tuple)) and len(wp) >= 2:
                    waypoints.append((wp[0], wp[1]))
                else:
                    waypoints.append(wp)
        
        return Movement(
            type=movement_dict["type"],
            from_pos=from_pos,
            to_pos=to_pos,
            style=movement_dict.get("style", "solid"),
            label=movement_dict.get("label", ""),
            waypoints=waypoints
        )
    except Exception as e:
        logger.error(f"Failed to convert movement: {e}")
        return None


def dict_to_zone(zone_dict: Dict[str, Any]) -> Optional[Zone]:
    """Convert dict to Zone object with error handling."""
    try:
        # Required fields
        required = ["type", "shape", "bounds"]
        if not all(k in zone_dict for k in required):
            logger.warning(f"Zone missing required fields: {zone_dict}")
            return None
        
        return Zone(
            type=zone_dict["type"],
            shape=zone_dict["shape"],
            bounds=zone_dict["bounds"],
            team=zone_dict.get("team", "neutral"),
            opacity=zone_dict.get("opacity", 0.3),
            color=zone_dict.get("color", "blue"),
            label=zone_dict.get("label", "")
        )
    except Exception as e:
        logger.error(f"Failed to convert zone: {e}")
        return None


def dict_to_equipment(eq_dict: Dict[str, Any]) -> Optional[Equipment]:
    """Convert dict to Equipment object."""
    try:
        return Equipment(
            type=eq_dict.get("type", "cone"),
            coordinates=eq_dict.get("coordinates", {"x": 0, "y": 0}),
            count=eq_dict.get("count", 1),
            color=eq_dict.get("color", "orange"),
            size=eq_dict.get("size", "medium"),
            label=eq_dict.get("label", None)
        )
    except Exception as e:
        logger.error(f"Failed to convert equipment: {e}")
        return None

def dict_to_diagram_spec(spec_dict: Dict[str, Any]) -> Optional[DiagramSpec]:
    """
    Convert dict to DiagramSpec object with robust error handling.
    
    Args:
        spec_dict: Dictionary representation of diagram spec
        
    Returns:
        DiagramSpec object or None if conversion fails
    """
    try:
        # Convert players
        players = []
        for p in spec_dict.get("players", []):
            if isinstance(p, dict):
                player = dict_to_player(p)
                if player:
                    players.append(player)
            elif hasattr(p, 'type'):  # Already a Player object
                players.append(p)
        
        # Convert movements
        movements = []
        for m in spec_dict.get("movements", []):
            if isinstance(m, dict):
                movement = dict_to_movement(m)
                if movement:
                    movements.append(movement)
            elif hasattr(m, 'type'):  # Already a Movement object
                movements.append(m)
        
        # Convert zones
        zones = []
        for z in spec_dict.get("zones", []):
            if isinstance(z, dict):
                zone = dict_to_zone(z)
                if zone:
                    zones.append(zone)
            elif hasattr(z, 'type'):  # Already a Zone object
                zones.append(z)
        
        # Convert equipment
        equipment = []
        for e in spec_dict.get("equipment", []):
            if isinstance(e, dict):
                eq = dict_to_equipment(e)
                if eq:
                    equipment.append(eq)
            elif hasattr(e, 'type'):  # Already an Equipment object
                equipment.append(e)
        
        # Convert annotations (can be strings or Annotation objects)
        annotations = []
        for a in spec_dict.get("annotations", []):
            if isinstance(a, str):
                # Create a simple Annotation object for string
                ann = Annotation(text=a, position={"x": 0, "y": -40})
                annotations.append(ann)
            elif isinstance(a, dict):
                # Convert position dict coordinates to proper format if needed
                position = a.get("position", {"x": 0, "y": -40})
                if isinstance(position, dict) and "x" in position and "y" in position:
                    # Position is already in correct format
                    pass
                else:
                    position = {"x": 0, "y": -40}
                
                ann = Annotation(
                    text=a.get("text", ""),
                    position=position,
                    size=a.get("size", "medium"),
                    style=a.get("style", "normal")
                )
                annotations.append(ann)
        
        # Create DiagramSpec
        return DiagramSpec(
            title=spec_dict.get("title", "Hockey Drill"),
            rink=spec_dict.get("rink", {"view": "offensive"}),
            players=players,
            movements=movements,
            zones=zones,
            annotations=annotations,
            equipment=equipment,
            metadata=spec_dict.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Failed to convert dict to DiagramSpec: {e}")
        return None


def validate_spec_dict(spec_dict: Dict[str, Any]) -> List[str]:
    """
    Validate a spec dictionary without full conversion.
    
    Args:
        spec_dict: Dictionary to validate
        
    Returns:
        List of validation issues
    """
    issues = []
    
    # Check required top-level fields
    if "players" not in spec_dict:
        issues.append("Missing 'players' field")
    elif not isinstance(spec_dict["players"], list):
        issues.append("'players' must be a list")
    
    if "movements" not in spec_dict:
        issues.append("Missing 'movements' field")
    elif not isinstance(spec_dict["movements"], list):
        issues.append("'movements' must be a list")
    
    # Validate players
    for i, player in enumerate(spec_dict.get("players", [])):
        if not isinstance(player, dict):
            issues.append(f"Player {i} is not a dictionary")
            continue
        
        player_label = player.get("label", player.get("position", f"Player {i}"))
        
        # Check required fields
        if "type" not in player:
            issues.append(f"{player_label}: Missing 'type' (forward/defense/goalie)")
        elif player["type"] not in ["forward", "defense", "goalie", "coach", "puck"]:
            issues.append(f"{player_label}: Invalid type '{player['type']}' (use: forward/defense/goalie)")
            
        if "position" not in player:
            issues.append(f"{player_label}: Missing 'position' (e.g., F1, D1, G)")
            
        if "coordinates" not in player:
            issues.append(f"{player_label}: Missing 'coordinates'")
        elif not isinstance(player["coordinates"], dict):
            issues.append(f"{player_label}: Coordinates must be a dict with x,y")
        elif "x" not in player["coordinates"] or "y" not in player["coordinates"]:
            missing = []
            if "x" not in player["coordinates"]: missing.append("x")
            if "y" not in player["coordinates"]: missing.append("y")
            issues.append(f"{player_label}: Coordinates missing {' and '.join(missing)}")
    
    # Validate movements
    for i, movement in enumerate(spec_dict.get("movements", [])):
        if not isinstance(movement, dict):
            issues.append(f"Movement {i} is not a dictionary")
            continue
        
        movement_label = movement.get("label", f"Movement {i}")
        
        if "type" not in movement:
            issues.append(f"{movement_label}: Missing 'type' (skate/pass/shot/carry)")
        elif movement["type"] not in ["skate", "pass", "shot", "carry", "pressure"]:
            issues.append(f"{movement_label}: Invalid type '{movement['type']}' (use: skate/pass/shot/carry)")
            
        if "from_pos" not in movement:
            issues.append(f"{movement_label}: Missing 'from_pos'")
        if "to_pos" not in movement:
            issues.append(f"{movement_label}: Missing 'to_pos'")
    
    return issues