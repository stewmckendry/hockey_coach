# Hockey Coordinate Mapping System

This document provides a comprehensive guide to the coordinate mapping system for the Hockey Diagram MCP Server.

## Overview

The coordinate mapping system provides precise NHL-regulation coordinates for all aspects of hockey tactical diagram generation:

- **Player Positions**: Exact coordinates for each position in different zones and roles
- **Named Areas**: Coordinates for common hockey areas (slot, point, corner, etc.)
- **Formation Templates**: Pre-defined coordinates for standard formations
- **Zone Boundaries**: Area definitions for tactical zones
- **Drill Positioning**: Standard setups for common drill types

## Coordinate System

The system uses NHL-regulation coordinates:

- **X-axis**: -100 (defensive end) to 100 (offensive end)
- **Y-axis**: -42.5 (left boards) to 42.5 (right boards)
- **Origin**: Center ice (0, 0)
- **Goal Lines**: X = ±89
- **Blue Lines**: X = ±25

### Hockey Convention Notes

- **Left Wing**: On the right side (+Y) when facing the offensive zone
- **Right Wing**: On the left side (-Y) when facing the offensive zone
- **Defensive Zone**: X < -25 (home team perspective)
- **Offensive Zone**: X > 25 (home team perspective)

## Core Functions

### 1. Player Coordinate Retrieval

```python
from coordinate_mapper import get_player_coordinate

# Get coordinates for specific position, zone, and role
coord = get_player_coordinate("C", "offensive", "primary")
# Returns: (60, 0)

coord = get_player_coordinate("LW", "offensive", "corner") 
# Returns: (85, -35)

coord = get_player_coordinate("LD", "defensive", "gap")
# Returns: (-60, -15)
```

**Available Positions**: C, LW, RW, LD, RD, G

**Available Zones**: offensive, defensive, neutral

**Available Roles** (vary by position):
- **Centers**: primary, faceoff, high, low, cycle, support, coverage, backcheck
- **Wings**: primary, corner, half_wall, net_front, cycle, faceoff, point, coverage, backcheck, wing, support
- **Defense**: primary, point, pinch, support, gap, corner, net_front, faceoff, retreat
- **Goalies**: primary, crease, challenge, deep

### 2. Area Coordinate Retrieval

```python
from coordinate_mapper import get_area_coordinate

# Get coordinates for named areas
slot = get_area_coordinate("slot")           # (75, 0)
left_point = get_area_coordinate("left_point")  # (25, -30)
crease = get_area_coordinate("crease")       # (86, 0)
```

**Available Areas**: slot, high_slot, low_slot, left_point, right_point, left_corner, right_corner, behind_net, crease, goal_mouth, etc.

### 3. Role Description Conversion

```python
from coordinate_mapper import convert_role_to_coordinate

# Convert natural language descriptions to coordinates
coord = convert_role_to_coordinate("C", "high slot", "offensive")
coord = convert_role_to_coordinate("LW", "left corner", "offensive") 
coord = convert_role_to_coordinate("RD", "point", "offensive")
```

### 4. Formation Coordinates

```python
from coordinate_mapper import get_formation_coordinates

# Get all player positions for a formation
coords = get_formation_coordinates("2-1-2_forecheck")
# Returns: {"F1": (80, -20), "F2": (80, 20), "F3": (40, 0), ...}

# Apply formation to existing players
from coordinate_mapper import adjust_for_formation

players = [
    {"position": "C", "x": 0, "y": 0, "team": "home"},
    {"position": "LW", "x": 0, "y": -25, "team": "home"},
    # ... more players
]

adjusted_players = adjust_for_formation(players, "2-1-2_forecheck")
```

**Available Formations**:
- `2-1-2_forecheck`
- `1-2-2_forecheck` 
- `1-3-1_forecheck`
- `1-3-1_powerplay`
- `overload_powerplay`
- `box_penalty_kill`
- `diamond_penalty_kill`
- `neutral_zone_trap`
- `breakout_strong_side`
- `breakout_weak_side`
- `cycle_offensive_zone`
- `center_ice_faceoff`
- `offensive_zone_faceoff`
- `defensive_zone_faceoff`

### 5. Drill Positioning

```python
from coordinate_mapper import get_drill_positioning

# Get standard positions for drill types
positions = get_drill_positioning("triangle_passing", player_count=3)
# Returns: [(69, -22.5), (85, 0), (69, 22.5)]

positions = get_drill_positioning("2v1_rush", player_count=4)
# Returns: [(-60, -20), (-60, 20), (-40, 0), (-89, 0)]
```

**Available Drill Types**:
- `triangle_passing` (3 players)
- `horseshoe_passing` (4 players)
- `shooting_drill` (6 players)
- `2v1_rush` (4 players)
- `3v2_rush` (6 players)
- `breakout_drill` (6 players)

### 6. Zone Boundaries

```python
from coordinate_mapper import get_zone_boundary

# Get zone boundary coordinates [x, y, width, height]
slot_bounds = get_zone_boundary("slot")
# Returns: [60, -15, 29, 30]

offensive_zone = get_zone_boundary("offensive_zone")
# Returns: [25, -42.5, 75, 85]
```

### 7. Utility Functions

```python
from coordinate_mapper import (
    find_nearest_area,
    get_relative_position,
    validate_coordinate,
    list_available_formations,
    list_available_areas,
    get_faceoff_dots
)

# Find nearest named area to coordinates
area = find_nearest_area(70, -20)  # Returns: "left_half_wall"

# Get position relative to another position
base_pos = (50, 0)
relative_pos = get_relative_position(base_pos, "north", distance=15)
# Returns: (50, 15)

# Validate coordinates (clamp to rink bounds)
valid_coord = validate_coordinate(150, 60)  # Returns: (100, 42.5)

# List available elements
formations = list_available_formations()
areas = list_available_areas()
faceoff_dots = get_faceoff_dots()
```

## Integration with Enhanced Parser

The coordinate mapping system is designed to work seamlessly with the enhanced parser:

```python
from enhanced_parser import EnhancedHockeyParser
from coordinate_mapper import coordinate_mapper

parser = EnhancedHockeyParser()

# The parser automatically uses coordinate_mapper functions for:
# 1. Converting role descriptions to exact coordinates
# 2. Applying formation-specific adjustments
# 3. Validating coordinate bounds
# 4. Zone-specific positioning
```

## Usage Examples

### Example 1: Basic Player Positioning

```python
# Position players for power play
center = get_player_coordinate("C", "offensive", "low")      # Net front
left_wing = get_player_coordinate("LW", "offensive", "half_wall")  # Half wall
right_wing = get_player_coordinate("RW", "offensive", "half_wall") # Half wall
left_d = get_player_coordinate("LD", "offensive", "point")    # Left point
right_d = get_player_coordinate("RD", "offensive", "point")   # Right point
```

### Example 2: Creating a Custom Formation

```python
# Define custom formation players
players = [
    {"position": "C", "x": 0, "y": 0, "team": "home"},
    {"position": "LW", "x": 0, "y": -25, "team": "home"},
    {"position": "RW", "x": 0, "y": 25, "team": "home"},
    {"position": "LD", "x": -25, "y": -20, "team": "home"},
    {"position": "RD", "x": -25, "y": 20, "team": "home"},
    {"position": "G", "x": -89, "y": 0, "team": "home"},
]

# Apply formation adjustments
formation_players = adjust_for_formation(players, "1-3-1_powerplay")
```

### Example 3: Setting up a Drill

```python
# Get positions for triangle passing drill
drill_positions = get_drill_positioning("triangle_passing", 3)

# Convert to player objects
drill_players = []
for i, (x, y) in enumerate(drill_positions):
    drill_players.append({
        "position": f"P{i+1}",  # P1, P2, P3
        "x": x,
        "y": y,
        "team": "home",
        "step": 1
    })
```

### Example 4: Zone-Specific Analysis

```python
# Get all offensive zone positions for centers
offensive_coords = coordinate_mapper.get_zone_specific_coordinates("offensive")
center_roles = offensive_coords.get("C", {})

print("Center positions in offensive zone:")
for role, coord in center_roles.items():
    print(f"  {role}: {coord}")
```

## Error Handling

The coordinate mapping system includes built-in validation and fallbacks:

1. **Coordinate Validation**: All coordinates are automatically clamped to rink boundaries
2. **Fallback Positioning**: If a specific role isn't found, basic positioning is used
3. **Formation Fallbacks**: Unknown formations return unchanged player lists
4. **Area Fallbacks**: Unknown areas return center ice coordinates (0, 0)

## Testing

Run the test suite to verify functionality:

```bash
cd /path/to/hockey_diagram_mcp
python test_coordinate_mapper.py
```

The test suite validates:
- Basic coordinate retrieval
- Role description conversion
- Formation coordinate generation
- Drill positioning
- Coordinate validation
- Available element listing

## Performance Notes

- All coordinate lookups are O(1) dictionary operations
- Formation adjustments are O(n) where n is the number of players
- The system pre-computes all standard positions for fast access
- Memory usage is minimal (< 1MB for all coordinate data)

## Extending the System

To add new formations, areas, or drill types:

1. **New Formations**: Add to `FORMATION_ADJUSTMENTS` dictionary
2. **New Areas**: Add to `RINK_AREAS` dictionary
3. **New Drill Types**: Add to `get_drill_positioning()` method
4. **New Roles**: Add to position-specific dictionaries in `POSITION_COORDINATES`

Example adding a new formation:

```python
FORMATION_ADJUSTMENTS["custom_formation"] = {
    "player1": {"base": "C", "zone": Zone.OFFENSIVE, "role": "primary", "adjustment": (0, 0)},
    "player2": {"base": "LW", "zone": Zone.OFFENSIVE, "role": "corner", "adjustment": (5, -5)},
    # ... more players
}
```