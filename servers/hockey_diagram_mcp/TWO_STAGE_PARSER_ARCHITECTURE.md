# Two-Stage Parser Architecture

## Overview

The Hockey Diagram MCP Server uses a sophisticated two-stage parsing approach to convert natural language hockey coaching instructions into precise tactical diagrams. This architecture separates semantic understanding from coordinate mapping, resulting in more accurate and consistent diagram generation.

## Architecture Diagram

```
Natural Language Input
        ↓
┌─────────────────────┐
│   Stage 1: Entity   │
│     Extraction      │
│  (GPT-4 Analysis)   │
└─────────────────────┘
        ↓
  Semantic Entities
  (Players, Movements,
   Zones, Formations)
        ↓
┌─────────────────────┐
│   Stage 2: Entity   │
│    to Coordinates   │
│  (GPT-4 Mapping)    │
└─────────────────────┘
        ↓
   Precise Coordinates
   (NHL Regulation)
        ↓
┌─────────────────────┐
│  Diagram Generator  │
│    (sportypy)       │
└─────────────────────┘
        ↓
    Hockey Diagram
```

## Stage 1: Entity Extraction

### Purpose
Extract semantic hockey entities from natural language without requiring coordinate knowledge.

### Input
Natural language prompt: `"2-1-2 forecheck with F1 pressuring behind net"`

### Output
Structured entities:
```json
{
  "diagram_type": "formation",
  "primary_focus": "forechecking pressure with F1 behind net",
  "formation": {
    "formation_name": "2-1-2_forecheck",
    "formation_type": "forecheck",
    "zone_focus": "offensive"
  },
  "players": [
    {
      "position": "C",
      "team": "home",
      "formation_role": "F1",
      "named_location": "behind_net",
      "tactical_role": "pressure"
    },
    // ... more players
  ],
  "movements": [
    {
      "from_player": "C",
      "to_location": "behind_net",
      "movement_type": "forechecking",
      "purpose": "apply_pressure"
    }
  ]
}
```

### Key Features
- Uses named locations (e.g., "behind_net", "slot", "point")
- Identifies tactical roles (F1, F2, F3 for forechecking)
- Captures movement purposes and types
- No coordinate knowledge required from LLM

## Stage 2: Coordinate Mapping

### Purpose
Convert semantic entities to precise NHL-regulation coordinates using defined pick lists.

### Input
Entities from Stage 1

### Output
Diagram specification with coordinates:
```json
{
  "players": [
    {"position": "C", "x": 95, "y": 0, "team": "home"},
    {"position": "RW", "x": 85, "y": 35, "team": "home"},
    // ... more players with exact coordinates
  ],
  "movements": [
    {
      "from_position": "C",
      "to_position": [95, 0],
      "movement_type": "forechecking"
    }
  ],
  "view": "offensive",
  "title": "2-1-2 Forecheck Formation"
}
```

### Coordinate System
- X-axis: -100 (defensive end) to 100 (offensive end)
- Y-axis: -42.5 (left boards) to 42.5 (right boards)
- Goal lines: X = ±89
- Blue lines: X = ±25
- All coordinates match NHL regulation rink dimensions

## Pick List Definitions

### Movement Types
- `pass`: Puck sent between players (dashed arrow)
- `skating`: Player movement without puck (solid arrow)
- `skating_with_puck`: Puck carrier movement (solid arrow + puck)
- `shot`: Shooting at goal (thick arrow)
- `forecheck`: Aggressive offensive pressure
- `backcheck`: Defensive tracking
- `support`: Movement to provide options (dotted arrow)

### Player Roles
- Standard positions: `C`, `RW`, `LW`, `LD`, `RD`, `G`
- Tactical roles: `F1`, `F2`, `F3`, `D1`, `D2`
- Opposition: `X1`, `X2`, `X3`, `X4`, `X5`, `XG`

### Named Locations
- `slot`: High-danger area (60-89, -15 to 15)
- `behind_net`: Behind goal line (95, 0)
- `left_point`/`right_point`: Blue line positions
- `left_corner`/`right_corner`: Corner areas
- [See full list in two_stage_parser.py]

## Error Handling & Fallbacks

### Parser Cascade
1. **Primary**: Two-stage parser (highest accuracy)
2. **Secondary**: Enhanced parser (good accuracy)
3. **Tertiary**: Preset-based parser (basic functionality)

### Error Recovery
- Invalid movement types are mapped to closest valid type
- Unknown locations default to sensible positions
- Missing formations use basic positioning
- All errors logged with detailed context

## Benefits

### Accuracy
- 100% NHL-regulation compliance
- Consistent positioning across diagrams
- No coordinate hallucination

### Flexibility
- Easily add new formations
- Support custom team systems
- Handle coaching-specific terminology

### Maintainability
- Clear separation of concerns
- Easy to debug each stage
- Simple to extend pick lists

## Usage Examples

### Basic Formation
```
Input: "Box penalty kill"
Stage 1: Identifies 4-player box formation
Stage 2: Maps to defensive zone coordinates
Output: Precise box positioning diagram
```

### Complex Play
```
Input: "Power play umbrella with movement from half-wall to slot"
Stage 1: Extracts umbrella formation + movement details
Stage 2: Maps half-wall → slot movement with exact coordinates
Output: Dynamic power play diagram with arrows
```

### Drill Sequence
```
Input: "3v2 rush drill from neutral zone"
Stage 1: Identifies drill type, player counts, starting zone
Stage 2: Positions players appropriately for drill
Output: Practice drill diagram with proper spacing
```

## Testing

### Unit Tests
- `test_two_stage_parser.py`: Tests entity extraction
- `test_coordinate_mapper.py`: Tests coordinate mapping
- `test_entity_extraction.py`: Tests entity models

### Integration Tests
- `test_integration_full.py`: End-to-end testing
- `test_two_stage_integration.py`: Parser integration
- `generate_all_test_diagrams.py`: Visual validation

## Future Enhancements

1. **Multi-step drills**: Support for sequential diagram states
2. **Animation support**: Generate frame sequences
3. **Custom formations**: User-defined tactical systems
4. **Advanced analytics**: Heat maps and pressure zones
5. **3D projections**: Perspective views for broadcasts