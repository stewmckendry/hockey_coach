"""
Comprehensive coordinate mapping system for hockey diagram generation.

This module provides detailed coordinate mappings for all player positions,
rink areas, and formation-specific adjustments to enable precise NHL-accurate
hockey tactical diagram generation.
"""

from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
import math
from zone_grid import zone_grid, ZoneArea
from offset_system import parse_offset, get_offset_description


class Zone(Enum):
    """Hockey rink zones."""
    OFFENSIVE = "offensive"
    DEFENSIVE = "defensive"
    NEUTRAL = "neutral"
    FULL = "full"


class Team(Enum):
    """Team designations."""
    HOME = "home"
    AWAY = "away"


@dataclass
class CoordinateMapping:
    """A coordinate with optional context."""
    x: float
    y: float
    zone: Optional[Zone] = None
    team: Optional[Team] = None
    description: Optional[str] = None


class HockeyCoordinateMapper:
    """
    Comprehensive coordinate mapping system for hockey diagrams.
    
    Provides precise NHL-regulation coordinates for:
    - Player positions by role and zone
    - Named rink areas
    - Formation-specific adjustments
    - Relative positioning
    
    Uses ZoneGrid system for intelligent zone-based positioning.
    """
    
    # NHL regulation rink dimensions and key points
    NHL_RINK = {
        # Rink boundaries
        "rink_length": 200,  # -100 to +100
        "rink_width": 85,    # -42.5 to +42.5
        
        # Goal lines
        "goal_line_home": -89,
        "goal_line_away": 89,
        
        # Blue lines
        "blue_line_defensive": -25,
        "blue_line_offensive": 25,
        
        # Center line
        "center_line": 0,
        
        # Face-off circle radius
        "faceoff_circle_radius": 15,
        
        # Goal dimensions
        "goal_width": 6,
        "goal_depth": 4,
        "crease_radius": 6,
    }
    
    # Zone-based position mapping - maps positions and roles to specific zones
    ZONE_POSITION_MAPPING = {
        # Center positions
        "C": {
            Zone.OFFENSIVE: {
                "primary": "off-center-left-mid-high",
                "faceoff": "off-center-left-low", 
                "high": "off-center-left-high",
                "low": "off-center-left-low",
                "cycle": "off-center-left-mid-low",
                "support": "off-center-left-mid-high",
                "net_front": "off-center-left-low",
            },
            Zone.DEFENSIVE: {
                "primary": "def-center-right-mid-high",
                "faceoff": "def-center-right-low",
                "high": "def-center-right-high", 
                "coverage": "def-center-right-mid-high",
                "backcheck": "neu-right-mid-high",
                "support": "def-center-right-mid-low",
            },
            Zone.NEUTRAL: {
                "primary": "neu-left-mid-low",
                "regroup": "neu-left-mid-low",
                "transition": "neu-right-mid-low",
                "faceoff": "neu-left-mid-low",
            },
        },
        
        # Left wing positions  
        "LW": {
            Zone.OFFENSIVE: {
                "primary": "off-center-left-mid-high",  # No off-left zones exist
                "corner": "off-center-left-low",
                "half_wall": "off-center-left-mid-low",
                "net_front": "off-center-left-low",
                "cycle": "off-center-left-mid-low",
                "faceoff": "off-center-left-low",
                "wing": "off-center-left-mid-high",
            },
            Zone.DEFENSIVE: {
                "primary": "def-left-mid-high",
                "corner": "def-left-low",
                "point": "def-left-high",
                "coverage": "def-left-mid-high",
                "backcheck": "def-left-mid-low",
                "support": "def-left-mid-low",
            },
            Zone.NEUTRAL: {
                "primary": "neu-left-mid-high",
                "wing": "neu-left-high", 
                "support": "neu-left-mid-low",
                "transition": "neu-left-mid-high",
            },
        },
        
        # Right wing positions
        "RW": {
            Zone.OFFENSIVE: {
                "primary": "off-right-mid-high",
                "corner": "off-right-low",
                "half_wall": "off-right-mid-low", 
                "net_front": "off-center-right-low",
                "cycle": "off-right-mid-low",
                "faceoff": "off-right-low",
                "wing": "off-right-mid-high",
            },
            Zone.DEFENSIVE: {
                "primary": "def-right-mid-high",
                "corner": "def-right-low",
                "point": "def-right-high",
                "coverage": "def-right-mid-high",
                "backcheck": "def-right-mid-low",
                "support": "def-right-mid-low",
            },
            Zone.NEUTRAL: {
                "primary": "neu-right-mid-high",
                "wing": "neu-right-high",
                "support": "neu-right-mid-low", 
                "transition": "neu-right-mid-high",
            },
        },
        
        # Left defense positions
        "LD": {
            Zone.OFFENSIVE: {
                "primary": "off-center-left-high",  # No off-left zones exist
                "point": "off-center-left-high",
                "pinch": "off-center-left-mid-high",
                "support": "off-center-left-high",
            },
            Zone.DEFENSIVE: {
                "primary": "def-left-mid-low",
                "gap": "def-left-mid-high", 
                "corner": "def-left-low",
                "net_front": "def-center-left-low",
                "faceoff": "def-left-low",
                "coverage": "def-left-mid-low",
            },
            Zone.NEUTRAL: {
                "primary": "neu-left-mid-low",
                "gap": "neu-left-mid-high",
                "retreat": "neu-left-low",
            },
        },
        
        # Right defense positions
        "RD": {
            Zone.OFFENSIVE: {
                "primary": "off-right-high",
                "point": "off-right-high",
                "pinch": "off-right-mid-high",
                "support": "off-right-high",
            },
            Zone.DEFENSIVE: {
                "primary": "def-right-mid-low",
                "gap": "def-right-mid-high",
                "corner": "def-right-low",
                "net_front": "def-center-right-low", 
                "faceoff": "def-right-low",
                "coverage": "def-right-mid-low",
            },
            Zone.NEUTRAL: {
                "primary": "neu-right-mid-low",
                "gap": "neu-right-mid-high",
                "retreat": "neu-right-low",
            },
        },
        
        # Goalie positions
        "G": {
            Zone.DEFENSIVE: {
                "primary": "def-center-right-low",
                "crease": "def-center-right-low", 
                "challenge": "def-center-right-low",
                "deep": "def-center-right-low",
            },
            Zone.NEUTRAL: {
                "primary": "def-center-right-low",
            },
            Zone.OFFENSIVE: {
                "primary": "def-center-right-low", 
            },
        },
    }
    
    # Formation-specific zone mappings - overrides for special formations
    FORMATION_ZONE_MAPPINGS = {
        "box_penalty_kill": {
            "high_left": {"position": "LW", "zone": "def-left-mid-high"},
            "high_right": {"position": "RW", "zone": "def-center-right-mid-high"},  # Fixed zone name
            "low_left": {"position": "LD", "zone": "def-center-left-low"},  # In front of net
            "low_right": {"position": "RD", "zone": "def-center-right-low"},  # In front of net
        },
        
        "diamond_penalty_kill": {
            "top": {"position": "C", "zone": "def-center-left-mid-high"},
            "left": {"position": "LW", "zone": "def-left-mid-low"},
            "right": {"position": "RW", "zone": "def-center-right-mid-low"},  # Fixed zone name
            "bottom": {"position": "LD", "zone": "def-center-left-low"},
        },
        
        "1-3-1_powerplay": {
            "net_front": {"position": "C", "zone": "off-center-left-low"},
            "left_wing": {"position": "LW", "zone": "off-center-left-mid-low"},  # Fixed zone name
            "right_wing": {"position": "RW", "zone": "off-right-mid-low"},
            "left_point": {"position": "LD", "zone": "off-center-left-high"},  # Fixed zone name
            "right_point": {"position": "RD", "zone": "off-right-high"},
        },
        
        "2-1-2_forecheck": {
            "F1": {"position": "LW", "zone": "off-center-left-mid-high"},  # Fixed zone name
            "F2": {"position": "RW", "zone": "off-right-mid-high"},
            "F3": {"position": "C", "zone": "neu-left-mid-high"},
            "D1": {"position": "LD", "zone": "neu-left-mid-low"},
            "D2": {"position": "RD", "zone": "neu-right-mid-low"},
        },
        
        "breakout_strong_side": {
            "center": {"position": "C", "zone": "def-center-left-mid-high"},
            "strong_wing": {"position": "LW", "zone": "neu-left-mid-high"}, 
            "weak_wing": {"position": "RW", "zone": "def-center-right-mid-low"},  # Fixed zone name
            "d_with_puck": {"position": "LD", "zone": "def-left-low"},
            "d_support": {"position": "RD", "zone": "def-center-right-mid-low"},  # Fixed zone name
        },
        
        "cycle_offensive_zone": {
            "puck_carrier": {"position": "LW", "zone": "off-center-left-low"},  # Fixed zone name
            "support_high": {"position": "C", "zone": "off-center-left-mid-high"},
            "support_low": {"position": "RW", "zone": "off-center-right-low"},
            "left_point": {"position": "LD", "zone": "off-center-left-high"},  # Fixed zone name
            "right_point": {"position": "RD", "zone": "off-right-high"},
        },
    }
    
    # Precise faceoff dot coordinates (NHL regulation)
    FACEOFF_DOTS = {
        "center": (0, 0),
        
        # Defensive zone (home team perspective)
        "defensive_left": (-69, 22.5),
        "defensive_right": (-69, -22.5),
        "defensive_center": (-69, 0),
        
        # Offensive zone (home team perspective)
        "offensive_left": (69, 22.5),
        "offensive_right": (69, -22.5),
        "offensive_center": (69, 0),
        
        # Neutral zone
        "neutral_left_defensive": (-20.5, 22.5),
        "neutral_right_defensive": (-20.5, -22.5),
        "neutral_left_offensive": (20.5, 22.5),
        "neutral_right_offensive": (20.5, -22.5),
    }
    
    # Named rink areas with precise coordinates
    RINK_AREAS = {
        # Core areas
        "slot": CoordinateMapping(75, 0, Zone.OFFENSIVE, description="Prime scoring area"),
        "high_slot": CoordinateMapping(50, 0, Zone.OFFENSIVE, description="High slot area"),
        "low_slot": CoordinateMapping(85, 0, Zone.OFFENSIVE, description="Low slot area"),
        "goal_mouth": CoordinateMapping(89, 0, Zone.OFFENSIVE, description="Goal mouth area"),
        "crease": CoordinateMapping(86, 0, Zone.OFFENSIVE, description="Goal crease"),
        "goal_crease": CoordinateMapping(86, 0, Zone.OFFENSIVE, description="Goal crease"),  # Alias for crease
        
        # Point positions (moved from y=25 to y=35 to be clearly inside the zone)
        "left_point": CoordinateMapping(35, 30, Zone.OFFENSIVE, description="Left point position"),
        "right_point": CoordinateMapping(35, -30, Zone.OFFENSIVE, description="Right point position"),
        "center_point": CoordinateMapping(35, 0, Zone.OFFENSIVE, description="Center point position"),
        
        # Board areas
        "left_half_wall": CoordinateMapping(60, 35, Zone.OFFENSIVE, description="Left half-wall"),
        "right_half_wall": CoordinateMapping(60, -35, Zone.OFFENSIVE, description="Right half-wall"),
        "left_corner": CoordinateMapping(85, 35, Zone.OFFENSIVE, description="Left corner"),
        "right_corner": CoordinateMapping(85, -35, Zone.OFFENSIVE, description="Right corner"),
        "behind_net": CoordinateMapping(95, 0, Zone.OFFENSIVE, description="Behind the net"),
        
        # Defensive positions
        "defensive_slot": CoordinateMapping(-75, 0, Zone.DEFENSIVE, description="Defensive slot"),
        "defensive_high_slot": CoordinateMapping(-50, 0, Zone.DEFENSIVE, description="Defensive high slot"),
        "defensive_left_point": CoordinateMapping(-25, 30, Zone.DEFENSIVE, description="Defensive left point"),
        "defensive_right_point": CoordinateMapping(-25, -30, Zone.DEFENSIVE, description="Defensive right point"),
        "defensive_left_corner": CoordinateMapping(-85, 35, Zone.DEFENSIVE, description="Defensive left corner"),
        "defensive_right_corner": CoordinateMapping(-85, -35, Zone.DEFENSIVE, description="Defensive right corner"),
        
        # Neutral zone
        "neutral_center": CoordinateMapping(0, 0, Zone.NEUTRAL, description="Center ice"),
        "neutral_left": CoordinateMapping(0, 25, Zone.NEUTRAL, description="Neutral zone left"),
        "neutral_right": CoordinateMapping(0, -25, Zone.NEUTRAL, description="Neutral zone right"),
        
        # Special areas
        "top_of_circles": CoordinateMapping(54, 0, Zone.OFFENSIVE, description="Top of face-off circles"),
        "hash_marks": CoordinateMapping(69, 0, Zone.OFFENSIVE, description="Hash marks"),
        "side_boards": CoordinateMapping(50, 42.5, description="Side boards"),
        "end_boards": CoordinateMapping(100, 0, description="End boards"),
        
        # Penalty boxes and benches (NHL regulation positions)
        "penalty_box_home": CoordinateMapping(-8, -40, Zone.NEUTRAL, description="Home team penalty box"),
        "penalty_box_away": CoordinateMapping(8, -40, Zone.NEUTRAL, description="Away team penalty box"), 
        "bench_home": CoordinateMapping(-25, 40, Zone.NEUTRAL, description="Home team bench"),
        "bench_away": CoordinateMapping(25, 40, Zone.NEUTRAL, description="Away team bench"),
    }
    
    # Position-specific coordinates by zone and role
    POSITION_COORDINATES = {
        # Center positions
        "C": {
            Zone.OFFENSIVE: {
                "primary": (60, 0),
                "faceoff": (69, 0),
                "high": (40, 0),
                "low": (80, 0),
                "cycle": (70, -10),
                "support": (50, 0),
            },
            Zone.DEFENSIVE: {
                "primary": (-60, 0),
                "faceoff": (-69, 0),
                "high": (-40, 0),
                "coverage": (-50, 0),
                "backcheck": (-30, 0),
            },
            Zone.NEUTRAL: {
                "primary": (0, 0),
                "regroup": (-10, 0),
                "transition": (10, 0),
            },
        },
        
        # Left wing positions
        "LW": {
            Zone.OFFENSIVE: {
                "primary": (70, -25),
                "corner": (85, -35),
                "half_wall": (60, -35),
                "net_front": (85, -15),
                "cycle": (80, -30),
                "faceoff": (69, -22.5),
            },
            Zone.DEFENSIVE: {
                "primary": (-70, -25),
                "corner": (-85, -35),
                "point": (-25, -30),
                "coverage": (-60, -20),
                "backcheck": (-40, -25),
            },
            Zone.NEUTRAL: {
                "primary": (0, -25),
                "wing": (-10, -35),
                "support": (10, -25),
            },
        },
        
        # Right wing positions
        "RW": {
            Zone.OFFENSIVE: {
                "primary": (70, 25),
                "corner": (85, 35),
                "half_wall": (60, 35),
                "net_front": (85, 15),
                "cycle": (80, 30),
                "faceoff": (69, 22.5),
            },
            Zone.DEFENSIVE: {
                "primary": (-70, 25),
                "corner": (-85, 35),
                "point": (-25, 30),
                "coverage": (-60, 20),
                "backcheck": (-40, 25),
            },
            Zone.NEUTRAL: {
                "primary": (0, 25),
                "wing": (-10, 35),
                "support": (10, 25),
            },
        },
        
        # Left defense positions
        "LD": {
            Zone.OFFENSIVE: {
                "primary": (25, -20),
                "point": (25, -30),
                "pinch": (40, -25),
                "support": (30, -15),
            },
            Zone.DEFENSIVE: {
                "primary": (-70, -20),
                "gap": (-60, -15),
                "corner": (-80, -30),
                "net_front": (-85, -10),
                "faceoff": (-69, -22.5),
            },
            Zone.NEUTRAL: {
                "primary": (-15, -20),
                "gap": (-5, -15),
                "retreat": (-20, -20),
            },
        },
        
        # Right defense positions
        "RD": {
            Zone.OFFENSIVE: {
                "primary": (25, 20),
                "point": (25, 30),
                "pinch": (40, 25),
                "support": (30, 15),
            },
            Zone.DEFENSIVE: {
                "primary": (-70, 20),
                "gap": (-60, 15),
                "corner": (-80, 30),
                "net_front": (-85, 10),
                "faceoff": (-69, 22.5),
            },
            Zone.NEUTRAL: {
                "primary": (-15, 20),
                "gap": (-5, 15),
                "retreat": (-20, 20),
            },
        },
        
        # Goalie positions
        "G": {
            Zone.DEFENSIVE: {
                "primary": (-89, 0),
                "crease": (-86, 0),
                "challenge": (-85, 0),
                "deep": (-90, 0),
            },
            Zone.NEUTRAL: {
                "primary": (-89, 0),  # Goalies stay in net
            },
            Zone.OFFENSIVE: {
                "primary": (-89, 0),  # Goalies stay in net
            },
        },
    }
    
    # Formation-specific coordinate adjustments
    FORMATION_ADJUSTMENTS = {
        "2-1-2_forecheck": {
            "F1": {"base": "LW", "zone": Zone.OFFENSIVE, "role": "primary", "adjustment": (10, 5)},
            "F2": {"base": "RW", "zone": Zone.OFFENSIVE, "role": "primary", "adjustment": (10, -5)},
            "F3": {"base": "C", "zone": Zone.NEUTRAL, "role": "support", "adjustment": (0, 0)},
            "D1": {"base": "LD", "zone": Zone.NEUTRAL, "role": "gap", "adjustment": (5, 0)},
            "D2": {"base": "RD", "zone": Zone.NEUTRAL, "role": "gap", "adjustment": (5, 0)},
        },
        
        "1-2-2_forecheck": {
            "F1": {"base": "C", "zone": Zone.OFFENSIVE, "role": "primary", "adjustment": (15, 0)},
            "F2": {"base": "LW", "zone": Zone.OFFENSIVE, "role": "support", "adjustment": (0, 0)},
            "F3": {"base": "RW", "zone": Zone.OFFENSIVE, "role": "support", "adjustment": (0, 0)},
            "D1": {"base": "LD", "zone": Zone.NEUTRAL, "role": "primary", "adjustment": (0, 0)},
            "D2": {"base": "RD", "zone": Zone.NEUTRAL, "role": "primary", "adjustment": (0, 0)},
        },
        
        "1-3-1_forecheck": {
            "F1": {"base": "C", "zone": Zone.OFFENSIVE, "role": "primary", "adjustment": (10, 0)},
            "F2": {"base": "LW", "zone": Zone.NEUTRAL, "role": "primary", "adjustment": (0, 0)},
            "F3": {"base": "RW", "zone": Zone.NEUTRAL, "role": "primary", "adjustment": (0, 0)},
            "D1": {"base": "LD", "zone": Zone.DEFENSIVE, "role": "primary", "adjustment": (0, 0)},
            "D2": {"base": "RD", "zone": Zone.DEFENSIVE, "role": "primary", "adjustment": (0, 0)},
        },
        
        "1-3-1_powerplay": {
            "net_front": {"base": "C", "zone": Zone.OFFENSIVE, "role": "low", "adjustment": (0, 0)},
            "left_wing": {"base": "LW", "zone": Zone.OFFENSIVE, "role": "half_wall", "adjustment": (0, 0)},
            "right_wing": {"base": "RW", "zone": Zone.OFFENSIVE, "role": "half_wall", "adjustment": (0, 0)},
            "left_point": {"base": "LD", "zone": Zone.OFFENSIVE, "role": "point", "adjustment": (0, -10)},
            "right_point": {"base": "RD", "zone": Zone.OFFENSIVE, "role": "point", "adjustment": (0, 10)},
        },
        
        "overload_powerplay": {
            "net_front": {"base": "C", "zone": Zone.OFFENSIVE, "role": "low", "adjustment": (5, -5)},
            "left_corner": {"base": "LW", "zone": Zone.OFFENSIVE, "role": "corner", "adjustment": (0, -10)},
            "right_half_wall": {"base": "RW", "zone": Zone.OFFENSIVE, "role": "half_wall", "adjustment": (15, -10)},
            "left_point": {"base": "LD", "zone": Zone.OFFENSIVE, "role": "point", "adjustment": (5, -10)},
            "right_point": {"base": "RD", "zone": Zone.OFFENSIVE, "role": "point", "adjustment": (5, 20)},
        },
        
        "box_penalty_kill": {
            # Box formation - hash mark depth, faceoff dot width (from MCP research)
            "high_left": {"base": "LW", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (8, -7)},
            "high_right": {"base": "RW", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (8, 7)},
            "low_left": {"base": "LD", "zone": Zone.DEFENSIVE, "role": "net_front", "adjustment": (3, -7)},
            "low_right": {"base": "RD", "zone": Zone.DEFENSIVE, "role": "net_front", "adjustment": (3, 7)},
        },
        
        "diamond_penalty_kill": {
            # Diamond shape protecting slot (from MCP research)
            "top": {"base": "C", "zone": Zone.DEFENSIVE, "role": "high", "adjustment": (10, 0)},
            "left": {"base": "LW", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (5, -15)},
            "right": {"base": "RW", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (5, 15)},
            "bottom": {"base": "LD", "zone": Zone.DEFENSIVE, "role": "net_front", "adjustment": (-5, 0)},
        },
        
        "wedge_penalty_kill": {
            # Triangle in slot + sweeper (from MCP research)
            "top": {"base": "C", "zone": Zone.DEFENSIVE, "role": "high", "adjustment": (5, 0)},
            "left_base": {"base": "LW", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (-5, -10)},
            "right_base": {"base": "RW", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (-5, 10)},
            "sweeper": {"base": "RD", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (15, 15)},
        },
        
        "neutral_zone_trap": {
            "trap_forward": {"base": "C", "zone": Zone.NEUTRAL, "role": "primary", "adjustment": (10, 0)},
            "left_winger": {"base": "LW", "zone": Zone.NEUTRAL, "role": "wing", "adjustment": (0, -10)},
            "right_winger": {"base": "RW", "zone": Zone.NEUTRAL, "role": "wing", "adjustment": (0, 10)},
            "left_defense": {"base": "LD", "zone": Zone.NEUTRAL, "role": "retreat", "adjustment": (0, 0)},
            "right_defense": {"base": "RD", "zone": Zone.NEUTRAL, "role": "retreat", "adjustment": (0, 0)},
        },
        
        "breakout_strong_side": {
            "center": {"base": "C", "zone": Zone.DEFENSIVE, "role": "support", "adjustment": (20, 0)},
            "strong_wing": {"base": "LW", "zone": Zone.NEUTRAL, "role": "wing", "adjustment": (25, -35)},
            "weak_wing": {"base": "RW", "zone": Zone.DEFENSIVE, "role": "support", "adjustment": (-10, 35)},
            "d_with_puck": {"base": "LD", "zone": Zone.DEFENSIVE, "role": "corner", "adjustment": (5, -15)},
            "d_support": {"base": "RD", "zone": Zone.DEFENSIVE, "role": "gap", "adjustment": (15, 10)},
        },
        
        "breakout_weak_side": {
            "center": {"base": "C", "zone": Zone.DEFENSIVE, "role": "support", "adjustment": (20, 0)},
            "weak_wing": {"base": "RW", "zone": Zone.NEUTRAL, "role": "wing", "adjustment": (25, 35)},
            "strong_wing": {"base": "LW", "zone": Zone.DEFENSIVE, "role": "support", "adjustment": (-10, -35)},
            "d_with_puck": {"base": "RD", "zone": Zone.DEFENSIVE, "role": "corner", "adjustment": (5, 15)},
            "d_support": {"base": "LD", "zone": Zone.DEFENSIVE, "role": "gap", "adjustment": (15, -10)},
        },
        
        "cycle_offensive_zone": {
            "puck_carrier": {"base": "LW", "zone": Zone.OFFENSIVE, "role": "corner", "adjustment": (0, -5)},
            "support_high": {"base": "C", "zone": Zone.OFFENSIVE, "role": "primary", "adjustment": (5, 0)},
            "support_low": {"base": "RW", "zone": Zone.OFFENSIVE, "role": "net_front", "adjustment": (5, 25)},
            "left_point": {"base": "LD", "zone": Zone.OFFENSIVE, "role": "point", "adjustment": (5, -20)},
            "right_point": {"base": "RD", "zone": Zone.OFFENSIVE, "role": "point", "adjustment": (5, 20)},
        },
        
        "center_ice_faceoff": {
            "center": {"base": "C", "zone": Zone.NEUTRAL, "role": "faceoff", "adjustment": (0, 0)},
            "left_wing": {"base": "LW", "zone": Zone.NEUTRAL, "role": "primary", "adjustment": (-5, 20)},
            "right_wing": {"base": "RW", "zone": Zone.NEUTRAL, "role": "primary", "adjustment": (-5, -20)},
            "left_defense": {"base": "LD", "zone": Zone.NEUTRAL, "role": "primary", "adjustment": (-25, 20)},
            "right_defense": {"base": "RD", "zone": Zone.NEUTRAL, "role": "primary", "adjustment": (-25, -20)},
        },
        
        "offensive_zone_faceoff": {
            "center": {"base": "C", "zone": Zone.OFFENSIVE, "role": "faceoff", "adjustment": (0, 0)},
            "left_wing": {"base": "LW", "zone": Zone.OFFENSIVE, "role": "faceoff", "adjustment": (0, 0)},
            "right_wing": {"base": "RW", "zone": Zone.OFFENSIVE, "role": "primary", "adjustment": (10, 35)},
            "left_defense": {"base": "LD", "zone": Zone.OFFENSIVE, "role": "point", "adjustment": (0, -10)},
            "right_defense": {"base": "RD", "zone": Zone.OFFENSIVE, "role": "point", "adjustment": (0, 10)},
        },
        
        "defensive_zone_faceoff": {
            "center": {"base": "C", "zone": Zone.DEFENSIVE, "role": "faceoff", "adjustment": (0, 0)},
            "left_wing": {"base": "LW", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (0, 0)},
            "right_wing": {"base": "RW", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (10, -35)},
            "left_defense": {"base": "LD", "zone": Zone.DEFENSIVE, "role": "faceoff", "adjustment": (0, 0)},
            "right_defense": {"base": "RD", "zone": Zone.DEFENSIVE, "role": "net_front", "adjustment": (-5, 10)},
        },
        
        # Additional defensive systems from MCP research
        "box_defensive_coverage": {
            # Box defensive zone coverage (5v5)
            "left_forward": {"base": "LW", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (10, -10)},
            "right_forward": {"base": "RW", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (10, 10)},
            "center": {"base": "C", "zone": Zone.DEFENSIVE, "role": "high", "adjustment": (15, 0)},
            "left_defense": {"base": "LD", "zone": Zone.DEFENSIVE, "role": "net_front", "adjustment": (-5, -10)},
            "right_defense": {"base": "RD", "zone": Zone.DEFENSIVE, "role": "net_front", "adjustment": (-5, 10)},
        },
        
        "left_wing_lock": {
            # Left wing lock system (from MCP research)
            "locked_wing": {"base": "LW", "zone": Zone.DEFENSIVE, "role": "primary", "adjustment": (-10, -5)},
            "center": {"base": "C", "zone": Zone.NEUTRAL, "role": "primary", "adjustment": (10, 0)},
            "right_wing": {"base": "RW", "zone": Zone.NEUTRAL, "role": "wing", "adjustment": (5, 10)},
            "left_defense": {"base": "LD", "zone": Zone.DEFENSIVE, "role": "primary", "adjustment": (0, 0)},
            "right_defense": {"base": "RD", "zone": Zone.DEFENSIVE, "role": "primary", "adjustment": (0, 0)},
        },
        
        "man_on_man_defense": {
            # Man-on-man coverage (from MCP research)
            "center": {"base": "C", "zone": Zone.DEFENSIVE, "role": "support", "adjustment": (5, 0)},
            "left_wing": {"base": "LW", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (0, -5)},
            "right_wing": {"base": "RW", "zone": Zone.DEFENSIVE, "role": "coverage", "adjustment": (0, 5)},
            "left_defense": {"base": "LD", "zone": Zone.DEFENSIVE, "role": "net_front", "adjustment": (-10, -8)},
            "right_defense": {"base": "RD", "zone": Zone.DEFENSIVE, "role": "corner", "adjustment": (5, 15)},
        },
        
        # Power play formations from MCP research
        "umbrella_powerplay": {
            # 1-3-1 umbrella formation with exact positions
            "center_point": {"base": "C", "zone": Zone.OFFENSIVE, "role": "high", "adjustment": (10, 0)},
            "left_half_wall": {"base": "LW", "zone": Zone.OFFENSIVE, "role": "half_wall", "adjustment": (-10, -5)},
            "right_half_wall": {"base": "RW", "zone": Zone.OFFENSIVE, "role": "half_wall", "adjustment": (-10, 5)},
            "left_point": {"base": "LD", "zone": Zone.OFFENSIVE, "role": "point", "adjustment": (0, -10)},
            "right_point": {"base": "RD", "zone": Zone.OFFENSIVE, "role": "point", "adjustment": (0, 10)},
        },
        
        "spread_powerplay": {
            # Spread formation utilizing full zone width
            "net_front": {"base": "C", "zone": Zone.OFFENSIVE, "role": "net_front", "adjustment": (0, 0)},
            "left_wing": {"base": "LW", "zone": Zone.OFFENSIVE, "role": "corner", "adjustment": (0, 0)},
            "right_wing": {"base": "RW", "zone": Zone.OFFENSIVE, "role": "corner", "adjustment": (0, 0)},
            "left_point": {"base": "LD", "zone": Zone.OFFENSIVE, "role": "point", "adjustment": (-5, -15)},
            "right_point": {"base": "RD", "zone": Zone.OFFENSIVE, "role": "point", "adjustment": (-5, 15)},
        },
    }
    
    # Zone boundary definitions [x, y, width, height]
    ZONE_BOUNDARIES = {
        "offensive_zone": [25, -42.5, 75, 85],
        "defensive_zone": [-100, -42.5, 75, 85],
        "neutral_zone": [-25, -42.5, 50, 85],
        "slot": [60, -15, 29, 30],
        "high_slot": [40, -20, 40, 40],
        "left_point_area": [20, -40, 10, 20],
        "right_point_area": [20, 20, 10, 20],
        "left_corner_area": [75, -42.5, 25, 20],
        "right_corner_area": [75, 22.5, 25, 20],
        "behind_net_area": [89, -10, 11, 20],
        "left_boards": [-100, -42.5, 200, 15],
        "right_boards": [-100, 27.5, 200, 15],
        "left_faceoff_circle": [54, -37.5, 30, 30],
        "right_faceoff_circle": [54, 7.5, 30, 30],
        "center_circle": [-15, -15, 30, 30],
    }
    
    def get_player_coordinate(
        self, 
        position: str, 
        zone: Union[Zone, str], 
        role: str = "primary",
        formation: Optional[str] = None
    ) -> Tuple[float, float]:
        """
        Get coordinates for a player position in a specific zone and role using ZoneGrid.
        
        Args:
            position: Player position (C, LW, RW, LD, RD, G)
            zone: Zone (offensive, defensive, neutral)
            role: Specific role within zone (primary, faceoff, corner, etc.)
            formation: Optional formation for specific adjustments
            
        Returns:
            Tuple of (x, y) coordinates
        """
        if isinstance(zone, str):
            zone = Zone(zone.lower())
        
        # Check for formation-specific zone mapping first
        if formation and formation in self.FORMATION_ZONE_MAPPINGS:
            formation_data = self.FORMATION_ZONE_MAPPINGS[formation]
            # Look for role-specific zone override
            for role_key, role_data in formation_data.items():
                if role_key == role or role_data.get("position") == position:
                    zone_name = role_data.get("zone")
                    if zone_name:
                        # Use zone grid for coordinate
                        x, y = zone_grid.get_zone_position(zone_name)
                        # Add small offset for formation-specific fine-tuning
                        offset_x, offset_y = self._get_formation_offset(formation, role_key, position)
                        return (x + offset_x, y + offset_y)
        
        # Use zone-based position mapping
        if position in self.ZONE_POSITION_MAPPING:
            zone_mapping = self.ZONE_POSITION_MAPPING[position].get(zone, {})
            zone_name = zone_mapping.get(role)
            
            if zone_name:
                # Get coordinates from zone grid
                x, y = zone_grid.get_zone_position(zone_name)
                
                # Apply small role-specific offset within zone if needed
                offset_x, offset_y = self._get_role_offset(position, role, zone)
                return (x + offset_x, y + offset_y)
        
        # Fallback to legacy hardcoded coordinates for backward compatibility
        if position in self.POSITION_COORDINATES:
            zone_coords = self.POSITION_COORDINATES[position].get(zone, {})
            base_coord = zone_coords.get(role)
            
            if base_coord:
                x, y = base_coord
                
                # Apply formation-specific adjustments if provided
                if formation and formation in self.FORMATION_ADJUSTMENTS:
                    formation_data = self.FORMATION_ADJUSTMENTS[formation]
                    # Look for position-specific adjustments
                    for adj_key, adj_data in formation_data.items():
                        if adj_data.get("base") == position and adj_data.get("zone") == zone:
                            if adj_data.get("role") == role:
                                adj_x, adj_y = adj_data.get("adjustment", (0, 0))
                                x += adj_x
                                y += adj_y
                                break
                
                return (x, y)
        
        # Final fallback to basic position mapping
        return self._get_fallback_coordinate(position, zone)
    
    def get_area_coordinate(self, area_name: str) -> Tuple[float, float]:
        """
        Get coordinates for a named rink area.
        
        Args:
            area_name: Name of the rink area
            
        Returns:
            Tuple of (x, y) coordinates
        """
        if area_name in self.RINK_AREAS:
            coord = self.RINK_AREAS[area_name]
            return (coord.x, coord.y)
        
        # Check faceoff dots
        if area_name in self.FACEOFF_DOTS:
            return self.FACEOFF_DOTS[area_name]
        
        # Return center ice as fallback
        return (0, 0)
    
    def get_zone_boundary(self, zone_name: str) -> List[float]:
        """
        Get boundary coordinates for a zone.
        
        Args:
            zone_name: Name of the zone
            
        Returns:
            List of [x, y, width, height] coordinates
        """
        return self.ZONE_BOUNDARIES.get(zone_name, [0, 0, 10, 10])
    
    def get_relative_position(
        self, 
        base_position: Tuple[float, float], 
        relative_to: str, 
        distance: float = 10.0,
        angle: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Get position relative to another position or area.
        
        Args:
            base_position: Base (x, y) coordinate
            relative_to: Direction (north, south, east, west, etc.) or area name
            distance: Distance from base position
            angle: Optional angle in degrees (0 = east, 90 = north)
            
        Returns:
            Tuple of (x, y) coordinates
        """
        base_x, base_y = base_position
        
        if angle is not None:
            # Use angle-based positioning
            rad = math.radians(angle)
            x = base_x + distance * math.cos(rad)
            y = base_y + distance * math.sin(rad)
            return (x, y)
        
        # Use directional positioning
        direction_map = {
            "north": (0, distance),
            "south": (0, -distance),
            "east": (distance, 0),
            "west": (-distance, 0),
            "northeast": (distance * 0.707, distance * 0.707),
            "northwest": (-distance * 0.707, distance * 0.707),
            "southeast": (distance * 0.707, -distance * 0.707),
            "southwest": (-distance * 0.707, -distance * 0.707),
        }
        
        if relative_to.lower() in direction_map:
            dx, dy = direction_map[relative_to.lower()]
            return (base_x + dx, base_y + dy)
        
        # If relative_to is an area name, get its coordinate
        if relative_to in self.RINK_AREAS:
            target_coord = self.RINK_AREAS[relative_to]
            # Position at specified distance toward the target
            dx = target_coord.x - base_x
            dy = target_coord.y - base_y
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                unit_x = dx / length
                unit_y = dy / length
                return (base_x + unit_x * distance, base_y + unit_y * distance)
        
        return base_position
    
    def apply_zone_context(
        self, 
        position: str, 
        base_coordinate: Tuple[float, float], 
        context_zone: Union[Zone, str]
    ) -> Tuple[float, float]:
        """
        Apply zone-specific adjustments to coordinates.
        
        Args:
            position: Player position
            base_coordinate: Base (x, y) coordinate
            context_zone: Zone context for adjustments
            
        Returns:
            Adjusted (x, y) coordinates
        """
        if isinstance(context_zone, str):
            context_zone = Zone(context_zone.lower())
        
        x, y = base_coordinate
        
        # Zone-specific adjustments
        if context_zone == Zone.OFFENSIVE:
            # In offensive zone, adjust for attacking positioning
            if position in ["LW", "RW"]:
                # Wings play higher in offensive zone
                x = min(x + 5, 95)
            elif position == "C":
                # Center plays closer to net
                x = min(x + 10, 85)
        
        elif context_zone == Zone.DEFENSIVE:
            # In defensive zone, adjust for defensive positioning
            if position in ["LW", "RW"]:
                # Wings drop back more
                x = max(x - 10, -95)
            elif position in ["LD", "RD"]:
                # Defense plays tighter gaps
                x = max(x - 5, -90)
        
        # Ensure coordinates stay within rink bounds
        x = max(-100, min(100, x))
        y = max(-42.5, min(42.5, y))
        
        return (x, y)
    
    def convert_role_to_coordinate(
        self, 
        position: str, 
        location_description: str, 
        zone_hint: Optional[str] = None
    ) -> Tuple[float, float]:
        """
        Convert a role + location description to exact coordinates.
        
        Args:
            position: Player position (C, LW, RW, LD, RD, G)
            location_description: Description like "left corner", "high slot", "point"
            zone_hint: Optional zone context
            
        Returns:
            Tuple of (x, y) coordinates
        """
        # Normalize description
        desc_lower = location_description.lower().replace("-", " ").replace("_", " ")
        
        # Determine zone from description or hint
        zone = Zone.NEUTRAL  # default
        if zone_hint:
            zone = Zone(zone_hint.lower())
        elif any(word in desc_lower for word in ["offensive", "attacking", "o-zone"]):
            zone = Zone.OFFENSIVE
        elif any(word in desc_lower for word in ["defensive", "defending", "d-zone"]):
            zone = Zone.DEFENSIVE
        elif any(word in desc_lower for word in ["neutral", "center ice", "n-zone"]):
            zone = Zone.NEUTRAL
        
        # Map description to role
        role_map = {
            "corner": "corner",
            "half wall": "half_wall",
            "point": "point",
            "slot": "primary" if "high" in desc_lower else "low",
            "high slot": "high",
            "low slot": "low",
            "net front": "net_front",
            "behind net": "primary",
            "faceoff": "faceoff",
            "cycle": "cycle",
            "support": "support",
            "coverage": "coverage",
            "gap": "gap",
            "crease": "crease",
            "challenge": "challenge",
        }
        
        # Find matching role
        role = "primary"  # default
        for desc_key, role_value in role_map.items():
            if desc_key in desc_lower:
                role = role_value
                break
        
        return self.get_player_coordinate(position, zone, role)
    
    def _get_fallback_coordinate(self, position: str, zone: Zone) -> Tuple[float, float]:
        """Get fallback coordinate for position if not found in main mapping."""
        # Basic positioning by zone
        base_x = 0
        if zone == Zone.OFFENSIVE:
            base_x = 60
        elif zone == Zone.DEFENSIVE:
            base_x = -60
        
        # Basic positioning by player type
        base_y = 0
        if position == "LW":
            base_y = -25
        elif position == "RW":
            base_y = 25
        elif position == "LD":
            base_y = -20
        elif position == "RD":
            base_y = 20
        elif position == "G":
            base_x = -89
            base_y = 0
        
        return (base_x, base_y)
    
    def _get_formation_offset(self, formation: str, role_key: str, position: str) -> Tuple[float, float]:
        """Get small offset for formation-specific fine-tuning within zones."""
        # Formation-specific offsets for precise positioning within zones
        formation_offsets = {
            "box_penalty_kill": {
                "high_left": (-2, -3),
                "high_right": (-2, 3),
                "low_left": (2, -2),
                "low_right": (2, 2),
            },
            "diamond_penalty_kill": {
                "top": (3, 0),
                "left": (0, -3),
                "right": (0, 3),
                "bottom": (-2, 0),
            },
            "2-1-2_forecheck": {
                "F1": (2, -1),
                "F2": (2, 1),
                "F3": (0, 0),
                "D1": (0, -2),
                "D2": (0, 2),
            },
        }
        
        if formation in formation_offsets:
            return formation_offsets[formation].get(role_key, (0, 0))
        return (0, 0)
    
    def _get_role_offset(self, position: str, role: str, zone: Zone) -> Tuple[float, float]:
        """Get small offset for role-specific positioning within zones."""
        # Role-specific offsets for fine positioning within zones
        role_offsets = {
            "faceoff": (3, 0),  # Slightly forward for faceoffs
            "net_front": (4, 0),  # Closer to net
            "corner": (-2, -2),  # Slightly back and to boards 
            "point": (-3, 0),  # Slightly back from zone center
            "half_wall": (0, -3),  # Towards boards
            "cycle": (1, -1),  # Slight cycle position adjust
            "gap": (5, 0),  # Forward gap positioning
            "coverage": (-1, 0),  # Slightly back for coverage
        }
        
        return role_offsets.get(role, (0, 0))
    
    def get_position_with_descriptive_offset(
        self, 
        zone_name: str, 
        offset_description: Union[str, Dict[str, Union[float, str]]], 
        zone_type: Optional[str] = None
    ) -> Tuple[float, float]:
        """
        Get position coordinates using descriptive offset within a zone.
        
        Args:
            zone_name: Name of the zone
            offset_description: String description or dict with x, y, description
            zone_type: Zone context ("defensive", "offensive", "neutral")
            
        Returns:
            Tuple of (x, y) coordinates with offset applied
        """
        # Get base zone position
        base_x, base_y = zone_grid.get_zone_position(zone_name)
        
        # Parse offset description
        if isinstance(offset_description, dict):
            # Handle dict format: {"x": 5, "y": -3, "description": "deep near boards"}
            if "description" in offset_description:
                offset_x, offset_y = parse_offset(offset_description["description"], zone_type)
            else:
                offset_x = offset_description.get("x", 0)
                offset_y = offset_description.get("y", 0)
        else:
            # Handle string description
            offset_x, offset_y = parse_offset(offset_description, zone_type)
        
        return (base_x + offset_x, base_y + offset_y)
    
    def get_formation_coordinates(self, formation_name: str) -> Dict[str, Tuple[float, float]]:
        """
        Get all player coordinates for a specific formation using ZoneGrid.
        
        Args:
            formation_name: Name of the formation
            
        Returns:
            Dictionary mapping position names to coordinates
        """
        coordinates = {}
        
        # First try new zone-based formation mappings
        if formation_name in self.FORMATION_ZONE_MAPPINGS:
            formation_data = self.FORMATION_ZONE_MAPPINGS[formation_name]
            
            for role_key, role_data in formation_data.items():
                zone_name = role_data["zone"]
                position = role_data["position"]
                
                # Get zone coordinates
                x, y = zone_grid.get_zone_position(zone_name)
                
                # Apply formation-specific offset
                offset_x, offset_y = self._get_formation_offset(formation_name, role_key, position)
                coordinates[role_key] = (x + offset_x, y + offset_y)
        
        # Fallback to legacy formation adjustments for backward compatibility
        elif formation_name in self.FORMATION_ADJUSTMENTS:
            formation_data = self.FORMATION_ADJUSTMENTS[formation_name]
            
            for role_key, role_data in formation_data.items():
                position = role_data["base"]
                zone = role_data["zone"]
                role = role_data["role"]
                
                coord = self.get_player_coordinate(position, zone, role, formation_name)
                coordinates[role_key] = coord
        
        return coordinates
    
    def adjust_for_formation(self, players: List[Dict], formation_type: str) -> List[Dict]:
        """
        Adjust player positions based on formation type.
        
        Args:
            players: List of player dictionaries with position, x, y
            formation_type: Type of formation to apply
            
        Returns:
            List of adjusted player dictionaries
        """
        if formation_type not in self.FORMATION_ADJUSTMENTS:
            return players
        
        adjusted_players = []
        formation_data = self.FORMATION_ADJUSTMENTS[formation_type]
        
        for player in players:
            position = player.get("position", "")
            adjusted_player = player.copy()
            
            # Find matching formation role for this position
            for role_key, role_data in formation_data.items():
                if role_data.get("base") == position:
                    # Apply formation-specific coordinate
                    zone = role_data["zone"]
                    role = role_data["role"]
                    new_x, new_y = self.get_player_coordinate(position, zone, role, formation_type)
                    adjusted_player["x"] = new_x
                    adjusted_player["y"] = new_y
                    break
            
            adjusted_players.append(adjusted_player)
        
        return adjusted_players
    
    def get_tactical_zones(self) -> Dict[str, List[float]]:
        """
        Get all tactical zone boundaries for diagram generation.
        
        Returns:
            Dictionary of zone names to [x, y, width, height] boundaries
        """
        return self.ZONE_BOUNDARIES.copy()
    
    def find_nearest_area(self, x: float, y: float) -> str:
        """
        Find the nearest named area to given coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Name of nearest area
        """
        min_distance = float('inf')
        nearest_area = "center_ice"
        
        for area_name, coord in self.RINK_AREAS.items():
            distance = math.sqrt((coord.x - x)**2 + (coord.y - y)**2)
            if distance < min_distance:
                min_distance = distance
                nearest_area = area_name
        
        return nearest_area
    
    def get_drill_positioning(self, drill_type: str, player_count: int = 6) -> List[Tuple[float, float]]:
        """
        Get standard positioning for common drill types.
        
        Args:
            drill_type: Type of drill (passing, shooting, skating, etc.)
            player_count: Number of players to position
            
        Returns:
            List of (x, y) coordinates for player positions
        """
        drill_positions = {
            "triangle_passing": [
                (69, -22.5),   # Right faceoff dot
                (85, 0),       # Behind net
                (69, 22.5),    # Left faceoff dot
            ],
            
            "horseshoe_passing": [
                (69, -22.5),   # Right faceoff dot
                (85, 0),       # Behind net
                (69, 22.5),    # Left faceoff dot
                (40, 0),       # High slot
            ],
            
            "shooting_drill": [
                (0, -35),      # Left wing starting position
                (0, 35),       # Right wing starting position
                (50, 0),       # Center position
                (25, -30),     # Left point
                (25, 30),      # Right point
                (-89, 0),      # Goalie
            ],
            
            "2v1_rush": [
                (-60, -20),    # Attacking left wing
                (-60, 20),     # Attacking right wing
                (-40, 0),      # Defending player
                (-89, 0),      # Goalie
            ],
            
            "3v2_rush": [
                (-60, -25),    # Attacking left wing
                (-60, 0),      # Attacking center
                (-60, 25),     # Attacking right wing
                (-30, -15),    # Defending left
                (-30, 15),     # Defending right
                (-89, 0),      # Goalie
            ],
            
            "breakout_drill": [
                (-85, -30),    # Defense with puck
                (-70, 20),     # Support defense
                (-40, 0),      # Center
                (-20, -35),    # Strong side wing
                (-60, 35),     # Weak side wing
                (-89, 0),      # Goalie
            ],
        }
        
        if drill_type in drill_positions:
            positions = drill_positions[drill_type]
            return positions[:player_count]
        
        # Fallback: create basic formation
        return self._create_basic_formation(player_count)
    
    def _create_basic_formation(self, player_count: int) -> List[Tuple[float, float]]:
        """Create a basic formation for the given number of players."""
        positions = []
        
        if player_count >= 1:
            positions.append((-89, 0))  # Goalie
        if player_count >= 2:
            positions.append((-70, -20))  # Left defense
        if player_count >= 3:
            positions.append((-70, 20))   # Right defense
        if player_count >= 4:
            positions.append((-40, 0))    # Center
        if player_count >= 5:
            positions.append((-40, -25))  # Left wing
        if player_count >= 6:
            positions.append((-40, 25))   # Right wing
        
        # Add additional players in lines
        for i in range(6, player_count):
            line_x = -20 + (i - 6) * 20
            line_y = -30 + ((i - 6) % 3) * 30
            positions.append((line_x, line_y))
        
        return positions
    
    def get_zone_specific_coordinates(self, zone: Union[Zone, str]) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """
        Get all position coordinates for a specific zone.
        
        Args:
            zone: Zone to get coordinates for
            
        Returns:
            Dictionary of positions and their roles with coordinates
        """
        if isinstance(zone, str):
            zone = Zone(zone.lower())
        
        zone_coords = {}
        for position, zones in self.POSITION_COORDINATES.items():
            if zone in zones:
                zone_coords[position] = zones[zone]
        
        return zone_coords
    
    def validate_coordinate(self, x: float, y: float) -> Tuple[float, float]:
        """
        Validate and clamp coordinates to rink boundaries.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple of validated (x, y) coordinates
        """
        x = max(-100, min(100, x))
        y = max(-42.5, min(42.5, y))
        return (x, y)


# Create global instance for easy access
coordinate_mapper = HockeyCoordinateMapper()


def get_player_coordinate(position: str, zone: str, role: str = "primary", formation: str = None) -> Tuple[float, float]:
    """Convenience function to get player coordinates."""
    return coordinate_mapper.get_player_coordinate(position, zone, role, formation)


def get_area_coordinate(area_name: str) -> Tuple[float, float]:
    """Convenience function to get area coordinates."""
    return coordinate_mapper.get_area_coordinate(area_name)


def convert_role_to_coordinate(position: str, location: str, zone: str = None) -> Tuple[float, float]:
    """Convenience function to convert role description to coordinates."""
    return coordinate_mapper.convert_role_to_coordinate(position, location, zone)


def get_formation_coordinates(formation_name: str) -> Dict[str, Tuple[float, float]]:
    """Convenience function to get formation coordinates."""
    return coordinate_mapper.get_formation_coordinates(formation_name)


def adjust_for_formation(players: List[Dict], formation_type: str) -> List[Dict]:
    """Convenience function to adjust players for formation."""
    return coordinate_mapper.adjust_for_formation(players, formation_type)


def get_drill_positioning(drill_type: str, player_count: int = 6) -> List[Tuple[float, float]]:
    """Convenience function to get drill positioning."""
    return coordinate_mapper.get_drill_positioning(drill_type, player_count)


def get_zone_boundary(zone_name: str) -> List[float]:
    """Convenience function to get zone boundaries."""
    return coordinate_mapper.get_zone_boundary(zone_name)


def find_nearest_area(x: float, y: float) -> str:
    """Convenience function to find nearest area."""
    return coordinate_mapper.find_nearest_area(x, y)


def get_relative_position(base_position: Tuple[float, float], relative_to: str, distance: float = 10.0) -> Tuple[float, float]:
    """Convenience function to get relative position."""
    return coordinate_mapper.get_relative_position(base_position, relative_to, distance)


def validate_coordinate(x: float, y: float) -> Tuple[float, float]:
    """Convenience function to validate coordinates."""
    return coordinate_mapper.validate_coordinate(x, y)


def list_available_formations() -> List[str]:
    """Get list of all available formation names."""
    return list(coordinate_mapper.FORMATION_ADJUSTMENTS.keys())


def list_available_areas() -> List[str]:
    """Get list of all available area names."""
    return list(coordinate_mapper.RINK_AREAS.keys())


def list_available_zones() -> List[str]:
    """Get list of all available zone names."""
    return list(coordinate_mapper.ZONE_BOUNDARIES.keys())


def get_faceoff_dots() -> Dict[str, Tuple[float, float]]:
    """Get all faceoff dot coordinates."""
    return coordinate_mapper.FACEOFF_DOTS.copy()


def get_zone_specific_coordinates(zone: str) -> Dict[str, Dict[str, Tuple[float, float]]]:
    """Convenience function to get zone-specific coordinates."""
    return coordinate_mapper.get_zone_specific_coordinates(zone)


def get_zone_coordinate(zone_name: str, offset_x: float = 0, offset_y: float = 0) -> Tuple[float, float]:
    """Get coordinates for a zone using ZoneGrid."""
    return zone_grid.get_zone_position(zone_name, offset_x, offset_y)


def list_available_zones() -> List[str]:
    """Get list of all available zone names from ZoneGrid."""
    return zone_grid.list_all_zones()


def get_zone_by_coordinate(x: float, y: float) -> str:
    """Find which zone contains the given coordinate."""
    return zone_grid.get_zone_by_position(x, y)


def get_zone_bounds(zone_name: str) -> Tuple[float, float, float, float]:
    """Get boundary coordinates for a zone."""
    return zone_grid.get_zone_bounds(zone_name)