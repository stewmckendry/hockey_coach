"""
Reusable tactical elements and common formations for hockey diagrams.
Provides building blocks for standard plays and formations.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass

# Standard formations and their player positions
FORMATIONS = {
    "2-1-2_forecheck": {
        "description": "Standard 2-1-2 forecheck formation",
        "players": [
            {"position": "LW", "x": 60, "y": -20, "team": "home"},
            {"position": "RW", "x": 60, "y": 20, "team": "home"},
            {"position": "C", "x": 40, "y": 0, "team": "home"},
            {"position": "LD", "x": 10, "y": -15, "team": "home"},
            {"position": "RD", "x": 10, "y": 15, "team": "home"},
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "movements": [
            {"from_position": "LW", "to_position": [80, -15], "movement_type": "forecheck"},
            {"from_position": "RW", "to_position": [80, 15], "movement_type": "forecheck"},
        ],
        "zones": [
            {"zone_type": "pressure", "area": [50, -42.5, 50, 85], "team": "home"}
        ]
    },
    
    "1-2-2_forecheck": {
        "description": "1-2-2 aggressive forecheck",
        "players": [
            {"position": "C", "x": 70, "y": 0, "team": "home"},
            {"position": "LW", "x": 50, "y": -20, "team": "home"},
            {"position": "RW", "x": 50, "y": 20, "team": "home"},
            {"position": "LD", "x": 20, "y": -15, "team": "home"},
            {"position": "RD", "x": 20, "y": 15, "team": "home"},
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "movements": [
            {"from_position": "C", "to_position": [85, 0], "movement_type": "forecheck"},
        ]
    },
    
    "1-3-1_powerplay": {
        "description": "1-3-1 power play umbrella formation",
        "players": [
            {"position": "C", "x": 60, "y": 0, "team": "home"},
            {"position": "LW", "x": 40, "y": -30, "team": "home"},
            {"position": "RW", "x": 40, "y": 30, "team": "home"},
            {"position": "LD", "x": 30, "y": -20, "team": "home"},
            {"position": "RD", "x": 30, "y": 20, "team": "home"},
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "zones": [
            {"zone_type": "coverage", "area": "high_slot", "team": "home"}
        ]
    },
    
    "box_penalty_kill": {
        "description": "Box formation for penalty kill",
        "players": [
            {"position": "C", "x": -50, "y": -10, "team": "home"},
            {"position": "RW", "x": -50, "y": 10, "team": "home"},
            {"position": "LD", "x": -70, "y": -10, "team": "home"},
            {"position": "RD", "x": -70, "y": 10, "team": "home"},
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "zones": [
            {"zone_type": "coverage", "area": [-80, -20, 40, 40], "team": "home"}
        ]
    },
    
    "neutral_zone_trap": {
        "description": "1-3-1 neutral zone trap",
        "players": [
            {"position": "C", "x": 15, "y": 0, "team": "home"},
            {"position": "LW", "x": 0, "y": -25, "team": "home"},
            {"position": "RW", "x": 0, "y": 25, "team": "home"},
            {"position": "LD", "x": -15, "y": -15, "team": "home"},
            {"position": "RD", "x": -15, "y": 15, "team": "home"},
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "zones": [
            {"zone_type": "neutral", "area": [-25, -42.5, 50, 85], "team": "home"}
        ]
    },
    
    "breakout_strong_side": {
        "description": "Strong side breakout from defensive zone",
        "players": [
            {"position": "C", "x": -40, "y": 0, "team": "home"},
            {"position": "LW", "x": -20, "y": -35, "team": "home"},
            {"position": "RW", "x": -60, "y": 35, "team": "home"},
            {"position": "LD", "x": -85, "y": -20, "team": "home", "has_puck": True},
            {"position": "RD", "x": -70, "y": 10, "team": "home"},
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "movements": [
            {"from_position": "LD", "to_position": "RD", "movement_type": "pass"},
            {"from_position": "RW", "to_position": [-40, 35], "movement_type": "skating"},
            {"from_position": "LW", "to_position": [0, -35], "movement_type": "skating"},
        ]
    },
    
    "cycle_offensive_zone": {
        "description": "Offensive zone cycle play",
        "players": [
            {"position": "C", "x": 65, "y": 0, "team": "home"},
            {"position": "LW", "x": 85, "y": -30, "team": "home", "has_puck": True},
            {"position": "RW", "x": 70, "y": 25, "team": "home"},
            {"position": "LD", "x": 30, "y": -20, "team": "home"},
            {"position": "RD", "x": 30, "y": 20, "team": "home"},
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "movements": [
            {"from_position": "LW", "to_position": [85, -15], "movement_type": "skating"},
            {"from_position": "RW", "to_position": [85, -30], "movement_type": "skating"},
            {"from_position": "LW", "to_position": "RW", "movement_type": "pass"},
        ]
    },
    
    "overload_powerplay": {
        "description": "Overload power play formation",
        "players": [
            {"position": "C", "x": 70, "y": -5, "team": "home"},
            {"position": "LW", "x": 85, "y": -25, "team": "home"},
            {"position": "RW", "x": 75, "y": -15, "team": "home"},
            {"position": "LD", "x": 30, "y": -30, "team": "home"},
            {"position": "RD", "x": 30, "y": 20, "team": "home"},
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "zones": [
            {"zone_type": "pressure", "area": [60, -42.5, 40, 42.5], "team": "home"}
        ]
    }
}

# Common drill patterns
DRILL_PATTERNS = {
    "figure_8": {
        "description": "Figure 8 skating pattern around face-off circles",
        "cones": [
            {"x": -69, "y": -22.5},
            {"x": -69, "y": 22.5},
        ],
        "path": [
            {"x": -69, "y": 0},
            {"x": -69, "y": -22.5},
            {"x": -50, "y": -22.5},
            {"x": -69, "y": -22.5},
            {"x": -69, "y": 0},
            {"x": -69, "y": 22.5},
            {"x": -50, "y": 22.5},
            {"x": -69, "y": 22.5},
            {"x": -69, "y": 0},
        ]
    },
    
    "horseshoe": {
        "description": "Horseshoe passing drill",
        "positions": [
            {"x": 69, "y": -22.5},
            {"x": 85, "y": 0},
            {"x": 69, "y": 22.5},
            {"x": 40, "y": 0},
        ],
        "passes": [
            {"from": 0, "to": 1},
            {"from": 1, "to": 2},
            {"from": 2, "to": 3},
            {"from": 3, "to": 0},
        ]
    },
    
    "russian_circles": {
        "description": "Russian circles drill for agility",
        "circles": [
            {"center": {"x": -69, "y": -22.5}, "radius": 15},
            {"center": {"x": -69, "y": 22.5}, "radius": 15},
            {"center": {"x": 0, "y": 0}, "radius": 15},
            {"center": {"x": 69, "y": -22.5}, "radius": 15},
            {"center": {"x": 69, "y": 22.5}, "radius": 15},
        ]
    }
}

# Zone definitions for common hockey areas
HOCKEY_ZONES = {
    "offensive_zone": {"bounds": [25, -42.5, 75, 85], "description": "Offensive zone"},
    "defensive_zone": {"bounds": [-100, -42.5, 75, 85], "description": "Defensive zone"},
    "neutral_zone": {"bounds": [-25, -42.5, 50, 85], "description": "Neutral zone"},
    "slot": {"bounds": [60, -8, 25, 16], "description": "Slot area"},
    "high_slot": {"bounds": [40, -12, 30, 24], "description": "High slot area"},
    "left_point": {"bounds": [25, -35, 20, 15], "description": "Left point"},
    "right_point": {"bounds": [25, 20, 20, 15], "description": "Right point"},
    "left_corner": {"bounds": [80, -42.5, 20, 20], "description": "Left corner"},
    "right_corner": {"bounds": [80, 22.5, 20, 20], "description": "Right corner"},
    "behind_net": {"bounds": [89, -20, 11, 40], "description": "Behind the net"},
    "left_circle": {"bounds": [54, -37.5, 30, 30], "description": "Left face-off circle"},
    "right_circle": {"bounds": [54, 7.5, 30, 30], "description": "Right face-off circle"},
}

# Common player movement patterns
MOVEMENT_PATTERNS = {
    "swing": {
        "description": "D-to-D swing pass movement",
        "movements": [
            {"from": "LD", "to": "RD", "type": "pass"},
            {"from": "RD", "to": [0, 20], "type": "skating"},
        ]
    },
    
    "give_and_go": {
        "description": "Give and go passing play",
        "movements": [
            {"from": "C", "to": "RW", "type": "pass"},
            {"from": "C", "to": [20, 0], "type": "skating"},
            {"from": "RW", "to": "C", "type": "pass"},
        ]
    },
    
    "drop_pass": {
        "description": "Drop pass in neutral zone",
        "movements": [
            {"from": "C", "to": [-10, 0], "type": "pass"},
            {"from": "RW", "to": [-10, 0], "type": "skating"},
        ]
    },
    
    "cross_ice": {
        "description": "Cross-ice pass",
        "movements": [
            {"from": "LW", "to": "RW", "type": "pass"},
        ]
    }
}

def get_formation(name: str) -> Dict:
    """Get a formation by name."""
    return FORMATIONS.get(name, {})

def get_drill_pattern(name: str) -> Dict:
    """Get a drill pattern by name."""
    return DRILL_PATTERNS.get(name, {})

def get_zone(name: str) -> Dict:
    """Get zone bounds by name."""
    return HOCKEY_ZONES.get(name, {})

def get_movement_pattern(name: str) -> Dict:
    """Get a movement pattern by name."""
    return MOVEMENT_PATTERNS.get(name, {})

def list_available_elements() -> Dict[str, List[str]]:
    """List all available tactical elements."""
    return {
        "formations": list(FORMATIONS.keys()),
        "drill_patterns": list(DRILL_PATTERNS.keys()),
        "zones": list(HOCKEY_ZONES.keys()),
        "movement_patterns": list(MOVEMENT_PATTERNS.keys()),
    }