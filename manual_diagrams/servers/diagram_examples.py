"""
Hockey Diagram Examples and Patterns.
Provides examples and common patterns for each node type.
"""

PLAYER_EXAMPLES = {
    "basic_offensive_setup": {
        "description": "Standard offensive zone setup with 3 forwards and 2 defense",
        "example": [
            {"type": "forward", "position": "F1", "team": "home", "coordinates": {"x": 75, "y": -15}},
            {"type": "forward", "position": "F2", "team": "home", "coordinates": {"x": 75, "y": 15}},
            {"type": "forward", "position": "F3", "team": "home", "coordinates": {"x": 60, "y": 0}},
            {"type": "defense", "position": "D1", "team": "home", "coordinates": {"x": 35, "y": -20}},
            {"type": "defense", "position": "D2", "team": "home", "coordinates": {"x": 35, "y": 20}}
        ]
    },
    "powerplay_umbrella": {
        "description": "Power play umbrella formation",
        "example": [
            {"type": "forward", "position": "F1", "team": "home", "coordinates": {"x": 75, "y": -8}},
            {"type": "forward", "position": "F2", "team": "home", "coordinates": {"x": 75, "y": 8}},
            {"type": "forward", "position": "F3", "team": "home", "coordinates": {"x": 65, "y": 0}},
            {"type": "defense", "position": "D1", "team": "home", "coordinates": {"x": 45, "y": -15}},
            {"type": "defense", "position": "D2", "team": "home", "coordinates": {"x": 45, "y": 15}}
        ]
    },
    "breakout_pattern": {
        "description": "Basic breakout from defensive zone",
        "example": [
            {"type": "forward", "position": "F1", "team": "home", "coordinates": {"x": -75, "y": -20}},
            {"type": "forward", "position": "F2", "team": "home", "coordinates": {"x": -75, "y": 20}},
            {"type": "forward", "position": "F3", "team": "home", "coordinates": {"x": -40, "y": 0}},
            {"type": "defense", "position": "D1", "team": "home", "coordinates": {"x": -85, "y": -8}},
            {"type": "defense", "position": "D2", "team": "home", "coordinates": {"x": -85, "y": 8}}
        ]
    }
}

MOVEMENT_EXAMPLES = {
    "give_and_go": {
        "description": "Classic give-and-go play pattern",
        "example": [
            {
                "type": "pass",
                "from_pos": {"x": 50, "y": -15},
                "to_pos": {"x": 65, "y": 0},
                "style": "dashed"
            },
            {
                "type": "skate",
                "from_pos": {"x": 50, "y": -15},
                "to_pos": {"x": 75, "y": -10},
                "style": "solid",
                "waypoints": [{"x": 60, "y": -12}]
            },
            {
                "type": "pass",
                "from_pos": {"x": 65, "y": 0},
                "to_pos": {"x": 75, "y": -10},
                "style": "dashed"
            }
        ]
    },
    "cycle_pattern": {
        "description": "Offensive zone cycling movement",
        "example": [
            {
                "type": "carry",
                "from_pos": {"x": 85, "y": -20},
                "to_pos": {"x": 75, "y": -30},
                "style": "solid",
                "waypoints": [{"x": 82, "y": -25}]
            },
            {
                "type": "pass",
                "from_pos": {"x": 75, "y": -30},
                "to_pos": {"x": 60, "y": -15},
                "style": "dashed"
            }
        ]
    },
    "rush_pattern": {
        "description": "2-on-1 rush pattern",
        "example": [
            {
                "type": "carry",
                "from_pos": {"x": 0, "y": 0},
                "to_pos": {"x": 65, "y": 5},
                "style": "solid",
                "waypoints": [{"x": 30, "y": 2}, {"x": 50, "y": 4}]
            },
            {
                "type": "skate",
                "from_pos": {"x": -10, "y": 20},
                "to_pos": {"x": 70, "y": 15},
                "style": "solid"
            },
            {
                "type": "pass",
                "from_pos": {"x": 65, "y": 5},
                "to_pos": {"x": 70, "y": 15},
                "style": "dashed"
            }
        ]
    }
}

ZONE_EXAMPLES = {
    "practice_stations": {
        "description": "Practice drill stations with cones",
        "example": [
            {
                "id": "station1",
                "type": "area",
                "shape": "rectangle",
                "position": {"x": -50, "y": -20},
                "dimensions": {"width": 30, "height": 25},
                "style": {"fill": "rgba(255,255,0,0.2)", "stroke": "yellow"}
            },
            {
                "id": "station2",
                "type": "area",
                "shape": "rectangle",
                "position": {"x": 50, "y": 20},
                "dimensions": {"width": 30, "height": 25},
                "style": {"fill": "rgba(0,255,0,0.2)", "stroke": "green"}
            }
        ]
    },
    "shooting_lanes": {
        "description": "Highlighted shooting lanes",
        "example": [
            {
                "id": "lane1",
                "type": "highlight",
                "shape": "polygon",
                "points": [
                    {"x": 45, "y": -15},
                    {"x": 85, "y": -8},
                    {"x": 85, "y": -2},
                    {"x": 45, "y": -10}
                ],
                "style": {"fill": "rgba(255,0,0,0.3)", "stroke": "red"}
            }
        ]
    }
}

ANNOTATION_EXAMPLES = {
    "drill_instructions": {
        "description": "Text annotations for drill instructions",
        "example": [
            {
                "id": "title",
                "text": "2v1 Rush Drill",
                "position": {"x": 0, "y": -40},
                "style": {"fontSize": 16, "fontWeight": "bold"},
                "anchor": "middle"
            },
            {
                "id": "note1",
                "text": "F1 carries puck",
                "position": {"x": 30, "y": -5},
                "style": {"fontSize": 12},
                "anchor": "start"
            }
        ]
    },
    "phase_markers": {
        "description": "Phase or step markers",
        "example": [
            {
                "id": "phase1",
                "text": "1",
                "position": {"x": -50, "y": 0},
                "style": {"fontSize": 14, "fontWeight": "bold", "background": "white"},
                "anchor": "middle"
            },
            {
                "id": "phase2",
                "text": "2",
                "position": {"x": 0, "y": 0},
                "style": {"fontSize": 14, "fontWeight": "bold", "background": "white"},
                "anchor": "middle"
            }
        ]
    }
}

RINK_EXAMPLES = {
    "full_rink": {
        "description": "Full ice view for breakouts and rushes",
        "example": {
            "view": "full",
            "showDots": True,
            "showNets": True,
            "showCreases": True,
            "showCircles": True,
            "showLines": True
        }
    },
    "offensive_zone": {
        "description": "Offensive zone only for cycle and scoring plays",
        "example": {
            "view": "offensive",
            "showDots": True,
            "showNets": True,
            "showCreases": True,
            "showCircles": True
        }
    },
    "neutral_zone": {
        "description": "Neutral zone for regroup drills",
        "example": {
            "view": "neutral",
            "showDots": True,
            "showCircles": True,
            "showLines": True
        }
    }
}

COMMON_PATTERNS = {
    "players": {
        "tips": [
            "Use F1, F2, F3 for forwards, D1, D2 for defense",
            "Offensive zone: x=60 to x=85, defensive zone: x=-85 to x=-60",
            "Standard width: y=-42.5 to y=42.5",
            "Net front: x=85, y=0",
            "Point positions: x=45, y=±20",
            "Corners: x=85, y=±30"
        ],
        "coordinate_references": {
            "offensive_slot": {"x": 70, "y": 0},
            "offensive_left_circle": {"x": 69, "y": -22},
            "offensive_right_circle": {"x": 69, "y": 22},
            "left_point": {"x": 45, "y": -20},
            "right_point": {"x": 45, "y": 20},
            "behind_net": {"x": 90, "y": 0}
        }
    },
    "movements": {
        "tips": [
            "Use 'solid' for skating with puck, 'dashed' for passes",
            "Add waypoints for curved paths",
            "Typical pass is direct (no waypoints)",
            "Cycling uses waypoints near boards"
        ]
    },
    "zones": {
        "tips": [
            "Use 'area' type for practice stations",
            "Use 'highlight' for emphasis",
            "Keep opacity low (0.2-0.3) for overlays",
            "Rectangle and circle are most common shapes"
        ]
    }
}

def get_examples_for_node(node_type: str):
    """Get examples for a specific node type."""
    examples_map = {
        "players": PLAYER_EXAMPLES,
        "movements": MOVEMENT_EXAMPLES,
        "rink": RINK_EXAMPLES,
        "zones": ZONE_EXAMPLES,
        "annotations": ANNOTATION_EXAMPLES
    }
    
    patterns = COMMON_PATTERNS.get(node_type, {})
    examples = examples_map.get(node_type, {})
    
    return {
        "examples": examples,
        "patterns": patterns
    }