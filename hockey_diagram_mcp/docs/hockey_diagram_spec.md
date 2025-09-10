# Hockey Diagram Specification v2.0

## Overview
This specification defines the structure and elements used to create hockey tactical diagrams programmatically. The spec evolves with each iteration based on real coaching needs.

### Version History
- **v2.0 (2025-09-01)**: Major position system overhaul, enhanced movement patterns, smooth curve rendering
- **v1.1 (2025-08-27)**: Added `waypoints` field to Movement objects for smooth curved paths
- **v1.0 (2025-08-26)**: Initial specification based on Hockey Canada template

## Coordinate System
- **X-axis**: -100 to 100 (left to right)
- **Y-axis**: -42.5 to 42.5 (bottom to top)
- **Zones**:
  - Offensive zone: x > 25 (RIGHT side of rink)
  - Neutral zone: -25 ≤ x ≤ 25 (between blue lines)
  - Defensive zone: x < -25 (LEFT side of rink)

## Key Landmarks
```
Goal lines: x = ±89
Blue lines: x = ±25
Red line: x = 0
Faceoff dots: (±69, ±22.5)
Boards: y = ±42.5
Net front: x = ±86, y = 0
```

## Diagram Structure

### 1. Rink Configuration
```json
{
  "view": "full | offensive | defensive | neutral | half",
  "orientation": "horizontal | vertical",
  "show_zones": true | false,
  "show_faceoff_dots": true | false,
  "show_grid": false | true,
  "xlim": [-100, 100],  // Custom view bounds
  "ylim": [-42.5, 42.5]
}
```

### 2. Player Elements

#### Player Types
- **Coach**: `©` - Circle with C
- **Forwards**: `○` - Open circle (F1, F2, F3 labels)
- **Defenders**: `△` - Triangle (D1, D2 labels)
- **Goaltenders**: `◐` - Half-filled circle with G
- **X Players**: `X` - Opposition players (X1-X5)
- **Pucks**: `●` - Solid black circle

#### Player Object
```json
{
  "type": "forward | defense | goalie | coach | opponent | puck",
  "position": "C | LW | RW | LD | RD | G | X1-X5 | P1-P10",
  "coordinates": {"x": 0, "y": 0},
  "team": "home | away | neutral",
  "has_puck": false,
  "label": "optional custom label",
  "number": null
}
```

### 3. Movement Elements

#### Movement Types
- **Skating**: `———>` - Solid arrow line
- **Passing**: `• • • >` - Dotted arrow line
- **Shooting**: `- - - >` - Dashed arrow line
- **Carrying**: `～～～>` - Wavy arrow line
- **Backward**: `———>` - Solid with reverse indicator
- **Pressure**: `═══>` - Thick solid arrow

#### Movement Object
```json
{
  "type": "skate | pass | shot | carry | backward | lateral | pressure",
  "from_pos": {"x": 0, "y": 0} | "player_id",
  "to_pos": {"x": 0, "y": 0} | "player_id",
  "style": "solid | dashed | dotted | wavy",
  "waypoints": [[x1, y1], [x2, y2]],  // For curved paths
  "with_puck": false,
  "label": "optional label"
}
```

#### Movement Patterns (v2.0)
Enhanced patterns with automatic waypoint generation:
- **direct**: Straight line (passes/shots)
- **curve**: Gentle curve (standard skating)
- **cross_ice**: S-curve across ice (40+ Y-axis change)
- **drive**: Drive to net with defender avoidance
- **cycle**: Along boards cycling
- **rush**: Fast through neutral zone (60+ units)
- **rim**: Along boards behind net
- **dump**: High and deep into corner
- **chip**: Quick advance past defender
- **sauce**: Elevated pass over obstacle
- **wrap**: Around the net
- **bank**: Off the boards
- **stretch**: Long outlet pass
- **button_hook**: Curl back pattern
- **weave**: Serpentine through traffic

### 4. Zone Elements

#### Zone Types
- **Coverage zones**: Defensive responsibility areas
- **Pressure zones**: Forechecking areas
- **Equipment**: Cones, pylons, obstacles

#### Zone Object
```json
{
  "type": "coverage | pressure | lane | cone | pylon",
  "shape": "rectangle | circle | polygon",
  "bounds": {"x": 0, "y": 0, "width": 10, "height": 10} | {"radius": 5},
  "vertices": [[x1,y1], [x2,y2], [x3,y3]],  // For polygons
  "team": "home | away",
  "opacity": 0.2,
  "color": "blue | red | orange | gray",
  "label": "optional label"
}
```

### 5. Annotation Elements

#### Annotation Object
```json
{
  "text": "Annotation text",
  "position": {"x": 0, "y": 0},
  "size": "small | medium | large",
  "style": "normal | bold | italic",
  "anchor": "left | center | right"
}
```

## Position Reference System (v2.0)

### Offensive Zone Positions (x > 25)
See `position_schemas.md` for complete listing of 80+ positions including:
- Faceoff formations (home/away teams)
- Slot positions (high/mid/low with left/middle/right variations)
- Point positions (5 variations inside blue line)
- Corner and wall positions
- Net area positions

### Defensive Zone Positions (x < -25)
Mirror of offensive positions with role reversal

### Neutral Zone Positions (-25 ≤ x ≤ 25)
- Center ice positions
- Blue line positions
- Bench and penalty box areas

## Rendering Features (v2.0)

### Smooth Curve Rendering
- All movements with waypoints use CubicSpline interpolation
- Even single waypoint creates smooth curves
- 100 interpolation points for ultra-smooth paths

### Visual Hierarchy
- Z-ordering: Rink (0) → Zones (6) → Movements (8) → Players (10) → Equipment (11) → Goalie (12)
- Line styles properly differentiated
- Arrow heads indicate direction
- Labels positioned to avoid overlap

## Complete Example
```json
{
  "title": "2v1 Rush Drill",
  "rink": {
    "view": "full",
    "orientation": "horizontal"
  },
  "players": [
    {
      "type": "forward",
      "position": "F1",
      "coordinates": {"x": 0, "y": 0},
      "team": "home",
      "has_puck": true,
      "label": "F1"
    },
    {
      "type": "forward",
      "position": "F2",
      "coordinates": {"x": 0, "y": 30},
      "team": "home",
      "label": "F2"
    },
    {
      "type": "defense",
      "position": "D1",
      "coordinates": {"x": 50, "y": 0},
      "team": "away",
      "label": "D1"
    }
  ],
  "movements": [
    {
      "type": "carry",
      "from_pos": {"x": 0, "y": 0},
      "to_pos": {"x": 69, "y": 0},
      "waypoints": [[25, 5], [50, 0]],
      "style": "wavy",
      "with_puck": true,
      "label": "Drive"
    },
    {
      "type": "skate",
      "from_pos": {"x": 0, "y": 30},
      "to_pos": {"x": 69, "y": -20},
      "waypoints": [[35, 25], [60, 0]],
      "style": "solid",
      "label": "Support"
    }
  ],
  "zones": [
    {
      "type": "cone",
      "shape": "polygon",
      "vertices": [[40, 0], [42, -3], [38, -3]],
      "color": "orange",
      "opacity": 1.0
    }
  ],
  "annotations": [
    {
      "text": "2v1 Rush - Focus on timing",
      "position": {"x": 0, "y": -40},
      "size": "large",
      "style": "bold"
    }
  ],
  "metadata": {
    "drill_type": "rush",
    "skill_focus": "offensive_tactics",
    "age_group": "U15"
  }
}
```

## Tool Integration

### MCP Tools Available
1. `map_position_to_coordinates` - Convert natural language to coordinates
2. `map_movement_to_coordinates` - Generate movements with waypoints
3. `validate_diagram_spec_full` - Comprehensive validation
4. `generate_diagram` - Create PNG/SVG output

### Position Mapping Features
- Direct position matching (80+ positions per zone)
- LLM-based interpretation for complex descriptions
- Relative positioning ("5 units left of F1")
- Fuzzy matching with confidence scores

### Movement Mapping Features
- Automatic pattern detection
- LLM-suggested waypoints for complex movements
- Pattern aliases ("wrap around" → "wrap")
- Zone-aware adjustments

## Validation Rules
1. Players must be within rink bounds
2. Movements need valid start/end positions
3. Cross-ice movements should have waypoints
4. Zone positioning must match drill context
5. Equipment shouldn't overlap with players

## Best Practices
1. Use landmark positions for player placement
2. Always add waypoints for curved movements
3. Label key movements for clarity
4. Use appropriate movement patterns
5. Validate spec before generation
6. Review generated image for accuracy