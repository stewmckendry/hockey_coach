"""
Hockey Diagram Schema Definitions.
Centralized schemas for all diagram node types.
"""

from typing import Dict, Any

# Player schemas (matches main file format)
PLAYER_SCHEMA = {
    "type": "object",
    "required": ["type", "position", "team", "coordinates"],
    "properties": {
        "type": {"type": "string", "enum": ["forward", "defense", "goalie", "coach", "puck"]},
        "position": {"type": "string", "pattern": "^[FDG][0-9]?$|^COACH$|^P[0-9]+$"},
        "team": {"type": "string", "enum": ["home", "away", "neutral"]},
        "has_puck": {"type": "boolean"},  # Optional for puck type
        "coordinates": {
            "type": "object",
            "required": ["x", "y"],
            "properties": {
                "x": {"type": "number", "minimum": -100, "maximum": 100},
                "y": {"type": "number", "minimum": -42.5, "maximum": 42.5}
            }
        },
        "label": {"type": "string"}
    }
}

PLAYERS_SCHEMA = {
    "type": "array",
    "minItems": 1,
    "maxItems": 12,
    "items": PLAYER_SCHEMA
}

# Movement schemas (matches main file format)
MOVEMENT_SCHEMA = {
    "type": "object", 
    "required": ["type", "from_pos", "to_pos", "style"],
    "properties": {
        "type": {"type": "string", "enum": ["skate", "pass", "shot", "carry", "pressure"]},
        "from_pos": {
            "type": "object",
            "required": ["x", "y"],
            "properties": {
                "x": {"type": "number", "minimum": -100, "maximum": 100},
                "y": {"type": "number", "minimum": -42.5, "maximum": 42.5}
            }
        },
        "to_pos": {
            "type": "object",
            "required": ["x", "y"],
            "properties": {
                "x": {"type": "number", "minimum": -100, "maximum": 100},
                "y": {"type": "number", "minimum": -42.5, "maximum": 42.5}
            }
        },
        "style": {"type": "string", "enum": ["solid", "dashed", "dotted", "wavy"]},
        "waypoints": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["x", "y"],
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"}
                }
            }
        },
        "label": {"type": "string"}
    }
}

MOVEMENTS_SCHEMA = {
    "type": "array",
    "items": MOVEMENT_SCHEMA
}

# Rink schema
RINK_SCHEMA = {
    "type": "object",
    "required": ["view"],
    "properties": {
        "view": {"type": "string", "enum": ["full", "half", "offensive", "defensive", "neutral"]},
        "showDots": {"type": "boolean", "default": True},
        "showNets": {"type": "boolean", "default": True},
        "showCreases": {"type": "boolean", "default": True},
        "showCircles": {"type": "boolean", "default": True},
        "showLines": {"type": "boolean", "default": True},
        "showTrapezoid": {"type": "boolean", "default": False}
    }
}

# Zone schema
ZONE_SCHEMA = {
    "type": "object",
    "required": ["id", "type"],
    "properties": {
        "id": {"type": "string"},
        "type": {"type": "string", "enum": ["highlight", "boundary", "area"]},
        "shape": {"type": "string", "enum": ["rectangle", "circle", "polygon"]},
        "position": {
            "type": "object",
            "required": ["x", "y"],
            "properties": {
                "x": {"type": "number"},
                "y": {"type": "number"}
            }
        },
        "dimensions": {
            "type": "object",
            "properties": {
                "width": {"type": "number"},
                "height": {"type": "number"},
                "radius": {"type": "number"}
            }
        },
        "points": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["x", "y"],
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"}
                }
            }
        },
        "style": {
            "type": "object",
            "properties": {
                "fill": {"type": "string"},
                "stroke": {"type": "string"},
                "strokeWidth": {"type": "number"},
                "opacity": {"type": "number"}
            }
        },
        "label": {"type": "string"}
    }
}

ZONES_SCHEMA = {
    "type": "array",
    "items": ZONE_SCHEMA
}

# Annotation schema
ANNOTATION_SCHEMA = {
    "type": "object",
    "required": ["id", "text", "position"],
    "properties": {
        "id": {"type": "string"},
        "text": {"type": "string"},
        "position": {
            "type": "object",
            "required": ["x", "y"],
            "properties": {
                "x": {"type": "number"},
                "y": {"type": "number"}
            }
        },
        "style": {
            "type": "object",
            "properties": {
                "fontSize": {"type": "number"},
                "fontWeight": {"type": "string"},
                "fill": {"type": "string"},
                "background": {"type": "string"}
            }
        },
        "anchor": {"type": "string", "enum": ["start", "middle", "end"]}
    }
}

ANNOTATIONS_SCHEMA = {
    "type": "array",
    "items": ANNOTATION_SCHEMA
}

# Complete spec schema
DIAGRAM_SPEC_SCHEMA = {
    "type": "object",
    "required": ["players", "movements", "rink"],
    "properties": {
        "players": PLAYERS_SCHEMA,
        "movements": MOVEMENTS_SCHEMA,
        "rink": RINK_SCHEMA,
        "zones": ZONES_SCHEMA,
        "annotations": ANNOTATIONS_SCHEMA
    }
}

# Schema mapping
NODE_SCHEMAS = {
    "players": PLAYERS_SCHEMA,
    "movements": MOVEMENTS_SCHEMA,
    "rink": RINK_SCHEMA,
    "zones": ZONES_SCHEMA,
    "annotations": ANNOTATIONS_SCHEMA
}

# Enum definitions for quick reference
PLAYER_TYPES = ["forward", "defense", "goalie", "coach", "puck"]
MOVEMENT_TYPES = ["skate", "pass", "shot", "carry", "pressure"]
MOVEMENT_STYLES = ["solid", "dashed", "dotted", "wavy"]
RINK_VIEWS = ["full", "half", "offensive", "defensive", "neutral"]
ZONE_TYPES = ["cone", "pylon", "tire", "net", "line", "area"]
ZONE_SHAPES = ["rectangle", "circle", "polygon"]
TEXT_ANCHORS = ["start", "middle", "end"]