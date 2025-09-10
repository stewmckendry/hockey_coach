"""
Reusable tactical elements and common formations for hockey diagrams.
Provides building blocks for standard plays and formations.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass

# Standard formations and their player positions
FORMATIONS = {
    "2-1-2_forecheck": {
        "description": "2-1-2 forecheck - 2 forwards deep (F1 on puck, F2 supporting), 1 forward high slot, 2 D inside blue line",
        "players": [
            # F1 (First forward) - Deep on puck carrier
            {"position": "LW", "x": 82, "y": -10, "team": "home", "has_puck": False},
            # F2 (Second forward) - Deep support with offset
            {"position": "RW", "x": 75, "y": 15, "team": "home"},
            # F3 (Third forward/Center) - Mid/high slot coverage
            {"position": "C", "x": 45, "y": 0, "team": "home"},
            # D1 (Left Defense) - Inside blue line in offensive zone
            {"position": "LD", "x": 30, "y": -20, "team": "home"},
            # D2 (Right Defense) - Inside blue line in offensive zone
            {"position": "RD", "x": 30, "y": 20, "team": "home"},
            # Goaltender
            {"position": "G", "x": -89, "y": 0, "team": "home"},
            # Opposition puck carrier
            {"position": "C", "x": 85, "y": -8, "team": "away", "has_puck": True},
        ],
        "movements": [
            # F1 pressure movement towards puck
            {"from_position": "LW", "to_position": [85, -8], "movement_type": "forecheck"},
            # F2 supporting movement with angle
            {"from_position": "RW", "to_position": [80, 10], "movement_type": "skating"},
            # F3 reads and reacts from high position
            {"from_position": "C", "to_position": [50, -5], "movement_type": "skating"},
        ],
        "zones": [
            {"zone_type": "pressure", "area": [65, -42.5, 35, 85], "team": "home", "opacity": 0.15}
        ]
    },
    
    "1-2-2_forecheck": {
        "description": "1-2-2 forecheck - 1 forward deep on puck, 2 forwards mid/high slot flanking, 2 D inside blue line",
        "players": [
            # F1 (Center) - Deep on puck
            {"position": "C", "x": 80, "y": 0, "team": "home"},
            # F2 (Left Wing) - Mid/high slot left side
            {"position": "LW", "x": 45, "y": -20, "team": "home"},
            # F3 (Right Wing) - Mid/high slot right side
            {"position": "RW", "x": 45, "y": 20, "team": "home"},
            # D1 (Left Defense) - Inside blue line
            {"position": "LD", "x": 30, "y": -15, "team": "home"},
            # D2 (Right Defense) - Inside blue line
            {"position": "RD", "x": 30, "y": 15, "team": "home"},
            # Goaltender
            {"position": "G", "x": -89, "y": 0, "team": "home"},
            # Opposition puck carrier
            {"position": "D", "x": 85, "y": 0, "team": "away", "has_puck": True},
        ],
        "movements": [
            {"from_position": "C", "to_position": [85, 0], "movement_type": "forecheck"},
            {"from_position": "LW", "to_position": [50, -25], "movement_type": "skating"},
            {"from_position": "RW", "to_position": [50, 25], "movement_type": "skating"},
        ]
    },
    
    "1-3-1_powerplay": {
        "description": "1-3-1 power play - 1 D at blue line, 3 players spread at mid-slot, 1 F at net front/crease",
        "players": [
            # Net front presence
            {"position": "C", "x": 75, "y": 0, "team": "home"},
            # Left half-wall
            {"position": "LW", "x": 45, "y": -30, "team": "home"},
            # Right half-wall
            {"position": "RW", "x": 45, "y": 30, "team": "home"},
            # Point man (quarterback) - centered at blue line
            {"position": "LD", "x": 30, "y": 0, "team": "home"},
            # Bumper/high slot
            {"position": "RD", "x": 50, "y": 0, "team": "home"},
            # Goaltender
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "zones": [
            {"zone_type": "coverage", "area": "high_slot", "team": "home"}
        ]
    },
    
    "box_penalty_kill": {
        "description": "Box penalty kill - 2 F covering point in high slot, 2 D covering low slot",
        "players": [
            # F1 - High slot left (covering left point)
            {"position": "LW", "x": -45, "y": -15, "team": "home"},
            # F2 - High slot right (covering right point)
            {"position": "RW", "x": -45, "y": 15, "team": "home"},
            # D1 - Low slot left (net front coverage)
            {"position": "LD", "x": -65, "y": -12, "team": "home"},
            # D2 - Low slot right (net front coverage)
            {"position": "RD", "x": -65, "y": 12, "team": "home"},
            # Goaltender
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "zones": [
            {"zone_type": "coverage", "area": [-75, -25, 40, 50], "team": "home"}
        ]
    },
    
    "neutral_zone_trap": {
        "description": "Neutral zone trap - 1 F pressuring at offensive blue line, 2 F at red line flanking, 2 D at defensive blue line",
        "players": [
            # F1 - Pressuring at offensive blue line
            {"position": "C", "x": 23, "y": 0, "team": "home"},
            # F2 - Left side near red line
            {"position": "LW", "x": -2, "y": -25, "team": "home"},
            # F3 - Right side near red line
            {"position": "RW", "x": -2, "y": 25, "team": "home"},
            # D1 - At defensive blue line left
            {"position": "LD", "x": -23, "y": -15, "team": "home"},
            # D2 - At defensive blue line right
            {"position": "RD", "x": -23, "y": 15, "team": "home"},
            # Goaltender
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "zones": [
            {"zone_type": "neutral", "area": [-25, -42.5, 50, 85], "team": "home"}
        ]
    },
    
    "breakout_strong_side": {
        "description": "Strong side (UP) breakout - Winger on boards at hashmark, other winger near blue line wide, D in corner, C supporting",
        "players": [
            # Center - Supporting in middle for pass option
            {"position": "C", "x": -55, "y": -10, "team": "home"},
            # Strong side winger - On boards at hashmark
            {"position": "LW", "x": -69, "y": -38, "team": "home"},
            # Weak side winger - Near blue line wide
            {"position": "RW", "x": -30, "y": 38, "team": "home"},
            # Strong side D - In corner with puck
            {"position": "LD", "x": -85, "y": -38, "team": "home", "has_puck": True},
            # Weak side D - In front of net
            {"position": "RD", "x": -85, "y": 5, "team": "home"},
            # Goaltender
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "movements": [
            # UP pass to winger on boards
            {"from_position": "LD", "to_position": "LW", "movement_type": "pass"},
            # Center swings for support
            {"from_position": "C", "to_position": [-40, -15], "movement_type": "skating"},
            # Weak side winger moves up ice
            {"from_position": "RW", "to_position": [-10, 38], "movement_type": "skating"},
        ]
    },
    
    "cycle_offensive_zone": {
        "description": "Offensive zone cycle - C and winger cycling on one side, other winger in slot looking to get open",
        "players": [
            # Center - Part of cycle on strong side
            {"position": "C", "x": 75, "y": -20, "team": "home"},
            # Strong side winger - Deep in corner with puck
            {"position": "LW", "x": 85, "y": -35, "team": "home", "has_puck": True},
            # Weak side winger - In slot looking to get open
            {"position": "RW", "x": 65, "y": 5, "team": "home"},
            # Strong side D - Supporting from point
            {"position": "LD", "x": 30, "y": -25, "team": "home"},
            # Weak side D - Holding blue line
            {"position": "RD", "x": 30, "y": 20, "team": "home"},
            # Goaltender
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "movements": [
            # Cycle movement - winger to center
            {"from_position": "LW", "to_position": "C", "movement_type": "pass"},
            # Center continues cycle
            {"from_position": "C", "to_position": [85, -25], "movement_type": "skating"},
            # Winger replaces center position
            {"from_position": "LW", "to_position": [75, -20], "movement_type": "skating"},
        ]
    },
    
    "diamond_penalty_kill": {
        "description": "Diamond penalty kill - 1 F at defensive blue line, 1 D at crease, 1 F + 1 D mid-slot flanking",
        "players": [
            # F1 - At defensive blue line (top of diamond)
            {"position": "C", "x": -27, "y": 0, "team": "home"},
            # F2 - Mid slot left side
            {"position": "LW", "x": -50, "y": -15, "team": "home"},
            # D1 - In front of net/crease (bottom of diamond)
            {"position": "LD", "x": -80, "y": 0, "team": "home"},
            # D2 - Mid slot right side
            {"position": "RD", "x": -50, "y": 15, "team": "home"},
            # Goaltender
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "zones": [
            {"zone_type": "coverage", "area": [-85, -30, 60, 60], "team": "home"}
        ]
    },
    
    "defensive_zone_coverage": {
        "description": "Defensive zone coverage - Wingers cover point from hashmarks to blue line, D cover low, C supports all",
        "players": [
            # Center - Supporting all positions (high slot)
            {"position": "C", "x": -55, "y": 0, "team": "home"},
            # Left winger - Covering left point (hashmark to blue line)
            {"position": "LW", "x": -40, "y": -30, "team": "home"},
            # Right winger - Covering right point (hashmark to blue line)
            {"position": "RW", "x": -40, "y": 30, "team": "home"},
            # Left D - Low coverage (hashmark to behind net)
            {"position": "LD", "x": -75, "y": -20, "team": "home"},
            # Right D - Low coverage (hashmark to behind net)
            {"position": "RD", "x": -75, "y": 20, "team": "home"},
            # Goaltender
            {"position": "G", "x": -89, "y": 0, "team": "home"},
        ],
        "zones": [
            {"zone_type": "coverage", "area": [-100, -42.5, 75, 85], "team": "home", "opacity": 0.1}
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