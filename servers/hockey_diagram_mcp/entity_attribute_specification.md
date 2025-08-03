# Hockey Diagram Entity Attribute Value Specification

## Overview
This document defines comprehensive entity attribute value lists for hockey diagram parsing. These structured values ensure consistency, accuracy, and proper understanding of hockey tactical diagrams when parsed by LLM systems.

## 1. Player Roles and Positions

### 1.1 Home Team Positions
**Attribute**: `position` (for team: "home")

| Value | Description | Usage Context |
|-------|-------------|---------------|
| `C` | Center | Primary puck handler, face-off specialist, both offensive and defensive responsibilities |
| `RW` | Right Wing | Right side forward, covers right boards and corner areas |
| `LW` | Left Wing | Left side forward, covers left boards and corner areas |
| `LD` | Left Defense | Left side defenseman, covers left point and defensive responsibilities |
| `RD` | Right Defense | Right side defenseman, covers right point and defensive responsibilities |
| `G` | Goaltender | Goalie, positioned in goal crease area (typically x: -89 for home team) |

### 1.2 Away Team Positions
**Attribute**: `position` (for team: "away")

| Value | Description | Usage Context |
|-------|-------------|---------------|
| `X1` | First Opponent | Generic opposing player, typically center or key player |
| `X2` | Second Opponent | Generic opposing player, typically forward |
| `X3` | Third Opponent | Generic opposing player, typically forward |
| `X4` | Fourth Opponent | Generic opposing player, typically defenseman |
| `X5` | Fifth Opponent | Generic opposing player, typically defenseman |
| `XG` | Opposing Goaltender | Opposing goalie, positioned in goal crease (typically x: 89) |

### 1.3 Specialized Role Modifiers
**Attribute**: `has_puck` (boolean)

| Value | Description | Usage Context |
|-------|-------------|---------------|
| `true` | Player currently has puck possession | Shows active puck carrier with visual indicator |
| `false` | Player does not have puck | Standard player representation |

**Attribute**: `step` (integer, optional)

| Value | Description | Usage Context |
|-------|-------------|---------------|
| `1` | First step in drill sequence | Multi-step drill progressions |
| `2` | Second step in drill sequence | Sequential movement patterns |
| `3` | Third step in drill sequence | Complex drill progressions |
| `null` | No sequence step | Static formations or simple plays |

## 2. Team Designations

### 2.1 Team Assignment
**Attribute**: `team`

| Value | Description | Usage Context | Visual Representation |
|-------|-------------|---------------|----------------------|
| `home` | Home team (defending left goal) | Primary team being coached | Blue color (#1E40AF) |
| `away` | Away/opposing team (defending right goal) | Opposition or practice partner | Red color (#DC2626) |

## 3. Named Locations on Rink

### 3.1 Key Rink Landmarks
**Attribute**: `area` (for zones) or coordinate reference

| Value | Description | Coordinates (x, y) | Usage Context |
|-------|-------------|-------------------|---------------|
| `center_ice` | Center of rink | (0, 0) | Face-offs, neutral zone plays |
| `goal_line_home` | Home team goal line | (-89, y) | Defensive positioning |
| `goal_line_away` | Away team goal line | (89, y) | Offensive positioning |
| `blue_line_defensive` | Defensive blue line | (-25, y) | Zone transitions |
| `blue_line_offensive` | Offensive blue line | (25, y) | Zone entries |

### 3.2 Face-off Locations
**Attribute**: `area` (specific dot positions)

| Value | Description | Coordinates (x, y) | Usage Context |
|-------|-------------|-------------------|---------------|
| `defensive_dot_left` | Left defensive zone dot | (-69, -22.5) | Defensive zone face-offs |
| `defensive_dot_right` | Right defensive zone dot | (-69, 22.5) | Defensive zone face-offs |
| `offensive_dot_left` | Left offensive zone dot | (69, -22.5) | Offensive zone face-offs |
| `offensive_dot_right` | Right offensive zone dot | (69, 22.5) | Offensive zone face-offs |
| `neutral_dot_left` | Left neutral zone dot | (-20.5, -22.5) | Neutral zone face-offs |
| `neutral_dot_right` | Right neutral zone dot | (-20.5, 22.5) | Neutral zone face-offs |

### 3.3 Tactical Areas
**Attribute**: `area` (tactical zones)

| Value | Description | Bounds [x, y, width, height] | Usage Context |
|-------|-------------|------------------------------|---------------|
| `slot` | High-danger scoring area | [60, -15, 29, 30] | Offensive positioning, screening |
| `high_slot` | Outer scoring area | [40, -20, 40, 40] | Support positioning |
| `left_point` | Left point position | [20, -40, 10, 20] | Power play, defensive coverage |
| `right_point` | Right point position | [20, 20, 10, 20] | Power play, defensive coverage |
| `left_corner` | Left corner area | [75, -42.5, 25, 20] | Puck retrieval, cycling |
| `right_corner` | Right corner area | [75, 22.5, 25, 20] | Puck retrieval, cycling |
| `behind_net` | Behind goal area | [89, -10, 11, 20] | Puck movement, support |
| `left_half_wall` | Left half-wall position | [60, -35, 10, 10] | Breakouts, cycling |
| `right_half_wall` | Right half-wall position | [60, 35, 10, 10] | Breakouts, cycling |
| `goal_crease` | Goal crease area | [89, -6, 6, 12] | Goaltender positioning |

## 4. Movement Types

### 4.1 Player Movement
**Attribute**: `movement_type`

| Value | Description | Visual Style | Usage Context |
|-------|-------------|--------------|---------------|
| `skating` | Player skating movement | Solid arrow | Position changes, forechecking |
| `pass` | Puck pass between players | Dashed arrow | Puck movement, playmaking |
| `shot` | Shot on goal | Thick solid arrow | Scoring attempts |
| `check` | Body check or pressure | Curved arrow | Defensive pressure |
| `support` | Support positioning | Dotted arrow | Off-puck movement |
| `forecheck` | Forechecking pressure | Curved gray arrow | Defensive pressure in offensive zone |

### 4.2 Arrow Styling
**Attribute**: `arrow_style`

| Value | Description | Visual Appearance | Usage Context |
|-------|-------------|------------------|---------------|
| `solid` | Solid line arrow | ——————> | Primary movements, skating |
| `dashed` | Dashed line arrow | ——  ——  ——> | Passes, secondary movements |
| `dotted` | Dotted line arrow | ·····> | Support movements, positioning |
| `thick` | Thick line arrow | ═══════> | Shots, primary attacks |

### 4.3 Movement Sequencing
**Attribute**: `sequence` (integer, optional)

| Value | Description | Usage Context |
|-------|-------------|---------------|
| `1` | First movement in sequence | Initial play setup |
| `2` | Second movement in sequence | Follow-up actions |
| `3` | Third movement in sequence | Completion or continuation |
| `null` | No sequence order | Simultaneous or single movements |

## 5. Zone Purposes and Types

### 5.1 Zone Types
**Attribute**: `zone_type`

| Value | Description | Visual Style | Usage Context |
|-------|-------------|--------------|---------------|
| `coverage` | Defensive coverage area | Light shading | Defensive responsibilities |
| `pressure` | Offensive pressure zone | Medium shading | Forechecking areas |
| `neutral` | Neutral zone control | Subtle shading | Transition areas |
| `position_area` | Specific position area | Highlighted zone | Teaching positions |

### 5.2 Zone Intensity
**Attribute**: `opacity` (float: 0.1 to 0.5)

| Value | Description | Visual Effect | Usage Context |
|-------|-------------|---------------|---------------|
| `0.1` | Very light shading | Barely visible overlay | Background reference |
| `0.2` | Light shading | Subtle area marking | Support zones |
| `0.3` | Medium shading | Clear area definition | Standard coverage |
| `0.4` | Strong shading | Prominent area marking | Key tactical zones |
| `0.5` | Heavy shading | Maximum emphasis | Critical areas |

## 6. View Preferences

### 6.1 Rink Views
**Attribute**: `view`

| Value | Description | Coordinate Range | Usage Context |
|-------|-------------|------------------|---------------|
| `full` | Complete rink view | (-100, -42.5) to (100, 42.5) | System overviews, full-ice plays |
| `offensive` | Offensive zone focus | (25, -42.5) to (100, 42.5) | Power plays, offensive tactics |
| `defensive` | Defensive zone focus | (-100, -42.5) to (-25, 42.5) | Penalty kills, defensive systems |
| `neutral` | Neutral zone focus | (-25, -42.5) to (25, 42.5) | Transitions, neutral zone trap |

## 7. Diagram Types

### 7.1 Diagram Classification
**Attribute**: `diagram_type`

| Value | Description | Key Characteristics | Usage Context |
|-------|-------------|-------------------|---------------|
| `formation` | Static tactical formation | Minimal movement, positional focus | System teaching, setups |
| `drill` | Practice drill sequence | Multiple steps, progression | Skill development, practice plans |
| `play` | Tactical play sequence | Flow-based, sequential movements | Game situations, strategy |
| `faceoff` | Face-off setup | Dot-centered, responsibility-focused | Special situations, draws |

## 8. Coordinate System Reference

### 8.1 Rink Coordinate System
- **X-axis**: -100 (defensive end) to +100 (offensive end)
- **Y-axis**: -42.5 (left side) to +42.5 (right side)
- **Origin**: Center ice (0, 0)
- **Orientation**: Defending left goal (home team), attacking right goal

### 8.2 Standard Position Coordinates

| Position | Home Team (x, y) | Away Team (x, y) | Context |
|----------|------------------|------------------|---------|
| Goaltender | (-89, 0) | (89, 0) | In goal crease |
| Defensemen | (-25, ±20) | (25, ±20) | At blue line |
| Centers | (0, 0) | (0, 0) | Center ice |
| Wingers | (±10, ±25) | (±10, ±25) | Wing positions |

## 9. Usage Guidelines for LLM Prompts

### 9.1 Prompt Structure
When using these attributes in LLM prompts, follow this structure:

```json
{
  "players": [
    {
      "position": "<value_from_section_1>",
      "x": <coordinate_value>,
      "y": <coordinate_value>,
      "team": "<value_from_section_2>",
      "has_puck": <boolean>,
      "step": <integer_or_null>
    }
  ],
  "movements": [
    {
      "from_position": "<position_value>",
      "to_position": [<x>, <y>] or "<position_value>",
      "movement_type": "<value_from_section_4>",
      "sequence": <integer_or_null>,
      "arrow_style": "<value_from_section_4>"
    }
  ],
  "zones": [
    {
      "zone_type": "<value_from_section_5>",
      "area": "<value_from_section_3>" or [<x>, <y>, <width>, <height>],
      "team": "<value_from_section_2>",
      "opacity": <float_value>
    }
  ],
  "view": "<value_from_section_6>",
  "diagram_type": "<value_from_section_7>"
}
```

### 9.2 Validation Rules
1. **Position Constraints**: All player positions must be within rink bounds
2. **Team Balance**: Ensure logical team assignments for tactical scenarios
3. **Movement Logic**: Movements should connect valid positions
4. **Zone Consistency**: Zone areas should align with tactical purpose
5. **View Appropriateness**: Select view based on diagram focus area

### 9.3 Common Patterns
- **Formations**: Static positions, minimal movements, emphasis on structure
- **Drills**: Multiple steps, sequence numbers, progression arrows
- **Plays**: Flow-based movements, tactical zones, situational context
- **Face-offs**: Dot-centered positioning, coverage responsibilities

This specification ensures consistent, accurate, and comprehensive hockey diagram generation through structured entity attribute definitions.