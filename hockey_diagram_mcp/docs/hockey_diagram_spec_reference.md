# Hockey Diagram Spec JSON Reference

## Overview

The hockey diagram spec is a JSON structure that defines all elements needed to create a tactical hockey diagram. The coordinate system uses:
- **X-axis**: -100 (left boards) to +100 (right boards)
- **Y-axis**: -42.5 (bottom boards) to +42.5 (top boards)
- **Origin (0,0)**: Center ice

## Complete Spec Structure

```json
{
  "title": "string",
  "description": "string", 
  "rink": {
    "features": ["array of strings"]
  },
  "players": [
    {
      "id": "string",
      "position": {"x": number, "y": number},
      "team": "string",
      "role": "string",
      "label": "string"
    }
  ],
  "movements": [
    {
      "type": "string",
      "from": "string or position",
      "to": "string or position",
      "style": "string",
      "label": "string"
    }
  ],
  "zones": [
    {
      "type": "string",
      "area": "object",
      "label": "string",
      "style": "string"
    }
  ],
  "annotations": [
    {
      "type": "string",
      "position": {"x": number, "y": number},
      "text": "string",
      "style": "string"
    }
  ]
}
```

## Field Definitions

### Root Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | No | Title of the diagram/drill |
| `description` | string | No | Brief description of the play or drill |
| `rink` | object | Yes | Rink configuration and features |
| `players` | array | Yes | Player positions and attributes |
| `movements` | array | No | Passes, carries, and skating paths |
| `zones` | array | No | Highlighted areas on the ice |
| `annotations` | array | No | Text labels and notes |

### Rink Object

```json
{
  "features": ["neutral_zone", "face_off_dots", "goals", "goal_creases"]
}
```

**Available Features:**
- `"neutral_zone"` - Shows neutral zone markings
- `"offensive_zone"` - Shows offensive zone
- `"defensive_zone"` - Shows defensive zone  
- `"face_off_dots"` - All faceoff circles and dots
- `"goals"` - Both goals
- `"goal_creases"` - Goalie creases
- `"center_ice"` - Center ice circle
- `"blue_lines"` - Blue lines
- `"red_line"` - Center red line

### Players Array

Each player object:

```json
{
  "id": "F1",
  "position": {"x": 69, "y": 22.5},
  "team": "offense",
  "role": "forward",
  "label": "F1"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., "F1", "D1", "G") |
| `position` | object | Yes | Coordinates on ice |
| `position.x` | number | Yes | X coordinate (-100 to 100) |
| `position.y` | number | Yes | Y coordinate (-42.5 to 42.5) |
| `team` | string | Yes | `"offense"`, `"defense"`, or `"neutral"` |
| `role` | string | No | `"forward"`, `"defenseman"`, `"goalie"`, `"coach"` |
| `label` | string | No | Display label (defaults to id) |

### Movements Array

Each movement object:

```json
{
  "type": "pass",
  "from": "F1",
  "to": {"x": 45, "y": 0},
  "style": "normal",
  "label": "outlet pass"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Movement type (see below) |
| `from` | string/object | Yes | Player ID or position |
| `to` | string/object | Yes | Player ID or position |
| `style` | string | No | Visual style (see below) |
| `label` | string | No | Text label for movement |

**Movement Types:**
- `"pass"` - Straight pass line
- `"carry"` - Puck carry/skate with puck
- `"skate"` - Skating without puck
- `"shot"` - Shot on goal

**Movement Styles:**
- `"normal"` - Standard line
- `"area"` - Area pass (dashed)
- `"drop"` - Drop pass
- `"saucer"` - Saucer pass
- `"backward"` - Backward movement

### Zones Array

Each zone object:

```json
{
  "type": "coverage",
  "area": {
    "x_min": 25,
    "x_max": 89,
    "y_min": -22.5,
    "y_max": 22.5
  },
  "label": "Defensive Coverage",
  "style": "solid"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | `"coverage"`, `"pressure"`, `"support"` |
| `area` | object | Yes | Rectangular area definition |
| `area.x_min` | number | Yes | Left boundary |
| `area.x_max` | number | Yes | Right boundary |
| `area.y_min` | number | Yes | Bottom boundary |
| `area.y_max` | number | Yes | Top boundary |
| `label` | string | No | Zone label |
| `style` | string | No | `"solid"`, `"dashed"`, `"highlighted"` |

### Annotations Array

Each annotation object:

```json
{
  "type": "text",
  "position": {"x": 0, "y": 40},
  "text": "2-1-2 Forecheck",
  "style": "title"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | `"text"`, `"arrow"`, `"circle"` |
| `position` | object | Yes | Position on ice |
| `text` | string | Yes* | Text content (*for text type) |
| `style` | string | No | `"title"`, `"normal"`, `"small"` |

## Ice Rink Landmarks & Common Positions

### Zone Boundaries

| Zone | X Range | Description |
|------|---------|-------------|
| **Defensive Zone** | -100 to -25 | Left side of rink |
| **Neutral Zone** | -25 to 25 | Center ice area |
| **Offensive Zone** | 25 to 100 | Right side of rink |

### Key Positions (Offensive Zone)

| Position | Coordinates | Description |
|----------|-------------|-------------|
| **Left Faceoff Dot** | (69, 22.5) | Offensive zone left circle |
| **Right Faceoff Dot** | (69, -22.5) | Offensive zone right circle |
| **Net Front** | (83, 0) | In front of goal |
| **Behind Net** | (89, 0) | Behind the goal |
| **Left Corner** | (89, 36) | Left corner boards |
| **Right Corner** | (89, -36) | Right corner boards |
| **High Slot** | (47, 0) | Between blue line and circles |
| **Low Slot** | (79, 0) | Between goal and circles |
| **Left Point** | (30, 20) | Left defense position |
| **Right Point** | (30, -20) | Right defense position |

### Key Positions (Defensive Zone)

| Position | Coordinates | Description |
|----------|-------------|-------------|
| **Left Faceoff Dot** | (-69, -22.5) | Defensive zone left circle |
| **Right Faceoff Dot** | (-69, 22.5) | Defensive zone right circle |
| **Net Front** | (-83, 0) | In front of own goal |
| **Behind Net** | (-89, 0) | Behind own goal |
| **Left Corner** | (-89, -36) | Defensive left corner |
| **Right Corner** | (-89, 36) | Defensive right corner |

### Neutral Zone Positions

| Position | Coordinates | Description |
|----------|-------------|-------------|
| **Center Ice** | (0, 0) | Center faceoff dot |
| **Left Wing Neutral** | (0, 30) | Left wing position |
| **Right Wing Neutral** | (0, -30) | Right wing position |

## Complete Example: 2-1-2 Forecheck

```json
{
  "title": "2-1-2 Neutral Zone Forecheck",
  "description": "Standard 2-1-2 forechecking formation in neutral zone",
  "rink": {
    "features": ["neutral_zone", "face_off_dots", "blue_lines"]
  },
  "players": [
    {
      "id": "F1",
      "position": {"x": 0, "y": 0},
      "team": "offense",
      "role": "forward",
      "label": "F1"
    },
    {
      "id": "F2",
      "position": {"x": -10, "y": -25},
      "team": "offense",
      "role": "forward",
      "label": "F2"
    },
    {
      "id": "F3",
      "position": {"x": -10, "y": 25},
      "team": "offense",
      "role": "forward",
      "label": "F3"
    },
    {
      "id": "D1",
      "position": {"x": -35, "y": -15},
      "team": "offense",
      "role": "defenseman",
      "label": "D1"
    },
    {
      "id": "D2",
      "position": {"x": -35, "y": 15},
      "team": "offense",
      "role": "defenseman",
      "label": "D2"
    }
  ],
  "movements": [
    {
      "type": "carry",
      "from": {"x": 25, "y": 0},
      "to": "F1",
      "style": "normal",
      "label": "puck carrier"
    }
  ],
  "zones": [
    {
      "type": "pressure",
      "area": {
        "x_min": -15,
        "x_max": 15,
        "y_min": -42.5,
        "y_max": 42.5
      },
      "label": "Pressure Zone",
      "style": "dashed"
    }
  ],
  "annotations": [
    {
      "type": "text",
      "position": {"x": 0, "y": 38},
      "text": "2-1-2 Formation",
      "style": "title"
    },
    {
      "type": "text",
      "position": {"x": 0, "y": -5},
      "text": "F1 pressures puck",
      "style": "small"
    }
  ]
}
```

## Validation Rules

1. **Coordinates**: All x,y values must be within rink bounds
   - X: -100 to 100
   - Y: -42.5 to 42.5

2. **Player IDs**: Must be unique within the spec

3. **Movement References**: `from` and `to` must reference valid player IDs or be coordinate objects

4. **Zone Areas**: Must have valid min/max boundaries where min < max

5. **Required Fields**: At minimum, spec must have:
   - `rink` object with `features` array
   - `players` array (can be empty for rink-only diagrams)

## Tips for Creating Specs

1. **Start Simple**: Begin with players and basic positions
2. **Use Landmarks**: Reference the position table for accurate placement
3. **Player Naming**: Use standard conventions (F1-F3 for forwards, D1-D2 for defense, G for goalie)
4. **Movement Order**: List movements in chronological order
5. **Zone Coverage**: Use zones to highlight areas of responsibility
6. **Annotations**: Add text to explain key concepts

## Common Patterns

### Power Play Setup (Umbrella)
```json
{
  "players": [
    {"id": "F1", "position": {"x": 79, "y": 0}, "label": "Net"},
    {"id": "F2", "position": {"x": 69, "y": 22.5}, "label": "Left"},
    {"id": "F3", "position": {"x": 69, "y": -22.5}, "label": "Right"},
    {"id": "D1", "position": {"x": 30, "y": -15}, "label": "LD"},
    {"id": "D2", "position": {"x": 30, "y": 15}, "label": "RD"}
  ]
}
```

### Breakout Pattern
```json
{
  "movements": [
    {"type": "carry", "from": "G", "to": "D1", "label": "1"},
    {"type": "pass", "from": "D1", "to": "D2", "label": "2"},
    {"type": "pass", "from": "D2", "to": "F1", "label": "3"},
    {"type": "carry", "from": "F1", "to": {"x": 0, "y": 30}, "label": "4"}
  ]
}
```

### Defensive Box
```json
{
  "zones": [
    {
      "type": "coverage",
      "area": {"x_min": -89, "x_max": -69, "y_min": -15, "y_max": 15},
      "label": "Box Coverage",
      "style": "solid"
    }
  ]
}
```

## Using with MCP Tools

When using the hockey diagram MCP tools:

1. **validate_diagram_spec_full**: Validates complete spec structure
2. **preview_diagram**: Shows ASCII preview of the diagram
3. **generate_diagram**: Creates the actual diagram files

The tools will provide helpful error messages if the spec is invalid.