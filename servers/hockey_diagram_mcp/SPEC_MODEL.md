# Hockey Diagram Specification Model

## Overview
This document defines the definitive specification model for hockey diagrams in the Hockey Diagram MCP Server. It clarifies the data flow, field requirements, and valid values for each component.

## Core Principle: Zones vs Coordinates
**IMPORTANT**: Specifications use **semantic zones** (labels like "slot", "point") NOT numeric coordinates. Coordinate conversion happens internally during diagram generation.

## Data Flow Architecture
```
User Input → Parser → Zone-Based Spec → generate_diagram_from_spec → Coordinate Conversion → Rendered Diagram
                            ↑
                    Interactive Editing
                    (process_diagram_feedback)
```

## Specification Model

### DiagramSpec (Root Object)
```typescript
interface DiagramSpec {
  // Required Fields
  title: string;              // Display title for the diagram
  players: Player[];          // Array of player positions (can be empty)
  
  // Optional Fields  
  movements?: Movement[];     // Array of movements/passes
  zones?: CoverageZone[];     // Coverage or highlighting zones
  view?: ViewType;            // Rink view perspective
  
  // Metadata (auto-generated)
  player_count?: number;      // Computed from players.length
  movement_count?: number;    // Computed from movements.length
}
```

### Player Object
```typescript
interface Player {
  // Required Fields
  position: PlayerRole;       // Role identifier (e.g., "F1", "C", "D1")
  zone: ZoneName;            // Semantic zone location
  team: TeamDesignation;     // "home" or "away"
  
  // Optional Fields
  has_puck?: boolean;        // Default: false
  label?: string;            // Custom display label
}

// Note: x/y coordinates are NEVER in specs, only generated internally
```

### Movement Object
```typescript
interface Movement {
  // Required Fields
  from_position: PlayerRole;  // Reference to player position
  to_position: PlayerRole;    // Reference to player position
  movement_type: MovementType; // Type of movement
  
  // Optional Fields
  label?: string;             // Movement label (e.g., "Pass 1")
}
```

### CoverageZone Object
```typescript
interface CoverageZone {
  // Required Fields
  zone_type: string;          // "coverage", "pressure", etc.
  area: ZoneName;            // Semantic zone name
  team: TeamDesignation;     // "home" or "away"
  
  // Optional Fields
  opacity?: number;          // 0.0-1.0, default: 0.2
}
```

## Valid Values (Picklists)

### PlayerRole Enum
```typescript
type PlayerRole = 
  // Forwards
  | "F1" | "F2" | "F3" | "F4" | "F5"
  | "C"   // Center
  | "LW"  // Left Wing  
  | "RW"  // Right Wing
  
  // Defense
  | "D1" | "D2" | "D3" | "D4"
  | "LD"  // Left Defense
  | "RD"  // Right Defense
  
  // Goalie
  | "G"   // Goalie
  
  // Generic
  | "X1" | "X2" | "X3" | "X4" | "X5"  // Opposing players
  | "P1" | "P2" | "P3" | "P4" | "P5"; // Generic players
```

### ZoneName Enum (Semantic Zones)
```typescript
type ZoneName = 
  // Offensive Zone
  | "offensive_left"
  | "offensive_right"
  | "offensive_slot"
  | "slot"           // Alias for offensive_slot
  | "high_slot"
  | "low_slot"
  | "point"
  | "left_point"
  | "right_point"
  | "left_circle"
  | "right_circle"
  | "goal_line"
  | "behind_net"
  | "left_corner"
  | "right_corner"
  
  // Neutral Zone
  | "neutral_left"
  | "neutral_center"
  | "neutral_right"
  | "center_ice"
  
  // Defensive Zone
  | "defensive_left"
  | "defensive_right"
  | "defensive_slot"
  | "defensive_point"
  | "defensive_left_circle"
  | "defensive_right_circle"
  | "defensive_goal_line"
  | "defensive_behind_net"
  | "defensive_left_corner"
  | "defensive_right_corner"
  
  // Special Zones
  | "bench"
  | "penalty_box";
```

### TeamDesignation Enum
```typescript
type TeamDesignation = "home" | "away";
```

### MovementType Enum
```typescript
type MovementType = 
  | "pass"
  | "shot"
  | "carry"
  | "skating"
  | "lateral"
  | "support";
```

### ViewType Enum
```typescript
type ViewType = 
  | "full"           // Full rink view
  | "offensive"      // Offensive zone only
  | "defensive"      // Defensive zone only
  | "neutral";       // Neutral zone only
```

## Parser Output Formats

### Two-Stage Parser Output
```json
{
  "title": "2-1-2 Forecheck",
  "view": "full",
  "players": [
    {
      "position": "F1",
      "zone": "offensive_slot",
      "team": "home",
      "has_puck": false
    },
    {
      "position": "F2",
      "zone": "offensive_left",
      "team": "home",
      "has_puck": false
    }
  ],
  "movements": [
    {
      "from_position": "F1",
      "to_position": "F2",
      "movement_type": "pass"
    }
  ]
}
```

### Legacy Parser Output (NOT RECOMMENDED)
Some legacy parsers may output x/y coordinates directly. These should be converted to zones when possible:
```json
{
  "players": [
    {
      "position": "F1",
      "x": 60,        // AVOID: Use zones instead
      "y": 0,         // AVOID: Use zones instead
      "team": "home"
    }
  ]
}
```

## Feedback Processor Requirements

The `process_diagram_feedback` tool expects:
1. **Input Spec**: Must have zone-based players array
2. **Validation**: Checks for required fields (position, zone OR x/y, team)
3. **Output Spec**: Returns updated zone-based spec

### Valid Feedback Spec Example
```json
{
  "title": "Power Play Setup",
  "players": [
    {
      "position": "F1",
      "zone": "point",
      "team": "home"
    },
    {
      "position": "D1", 
      "zone": "offensive_left",
      "team": "home"
    }
  ],
  "movements": []
}
```

## Common Issues and Solutions

### Issue: 422 Validation Error
**Cause**: Spec missing required fields or using wrong format
**Solution**: Ensure spec has:
- `players` array (even if empty)
- Each player has `position`, `zone` (or x/y), and `team`
- Movement references use `from_position`/`to_position`

### Issue: Spec Only Has Metadata
**Cause**: Frontend extracting wrong object
**Solution**: Extract spec from `generate_diagram_from_spec` tool arguments, not metadata

### Issue: Coordinates in Spec
**Cause**: Using legacy parser output
**Solution**: Use two-stage parser or convert coordinates to zones

## Testing Checklist

✓ Spec has `players` array
✓ Each player has `position`, `zone`, `team`
✓ Movements reference valid player positions
✓ Zone names are from valid picklist
✓ No x/y coordinates in spec (zones only)
✓ Frontend extracts from correct trace

## API Integration Points

1. **parse_hockey_formation** → Returns zone-based spec
2. **generate_diagram_from_spec** → Accepts zone-based spec, converts internally
3. **process_diagram_feedback** → Accepts and returns zone-based spec
4. **generate_from_spec** (API) → Wrapper accepting zone-based spec

## Summary

The definitive spec model is:
- **Zone-based** (semantic labels, not coordinates)
- **Player-centric** (players array is required)
- **Reference-based** (movements reference player positions)
- **Coordinate-free** (x/y conversion happens in generation only)

This ensures consistency across parsing, editing, and generation while maintaining semantic meaning for interactive modifications.