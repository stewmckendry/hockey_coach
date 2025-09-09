# Enhanced Hockey Diagram Agent Flow Plan

## Overview
This document outlines the enhanced flow for the Hockey Diagram Agent to provide better transparency, control, and accuracy in diagram generation. The new architecture introduces explicit intermediate tools that make the transformation process visible and debuggable.

## Current vs Enhanced Flow

### Current Flow (Opaque)
```
User Input → Agent → Research (if needed) → Natural Language Synthesis → Direct Diagram Generation
```
- The zone mapping happens inside the diagram generation tool
- No visibility into intermediate transformations
- Difficult to debug or adjust specific steps

### Enhanced Flow (Transparent)
```
User Input → Agent → Check Presets → Research → Synthesize → Map to Zones → Generate Coordinates → Render Diagram
```
- Each transformation is an explicit tool
- Full visibility and logging at each stage
- Easy to debug and adjust any step

## Detailed Tool Flow

### 1. User Input
```
Example: "Create a WHEEL breakout diagram"
```

### 2. Agent Checks Presets
- **Tool**: `parse_hockey_formation` (existing)
- **Input**: Formation name
- **Output**: If found → zone-mapped spec, If not found → "unknown formation"

### 3. Research Phase (for unknown formations)
- **Tools**: 
  - `search_hockey_tactics`
  - `search_hockey_drills`
  - `search_hockey_videos`
  - `web_search_exa` (if available)
- **Input**: Formation/concept name
- **Output**: Raw research results from multiple sources

### 4. Synthesize Research
- **Tool**: `synthesize_research_to_formation` (NEW)
- **Input**: Raw research results
- **Output**: Structured formation data
  ```
  {
    "name": "WHEEL Breakout",
    "description": "D-to-D pass behind net with center swinging...",
    "players_involved": ["LD", "RD", "C", "LW", "RW", "G"],
    "steps": [
      "1. LD retrieves puck in corner",
      "2. LD passes to RD behind net",
      "3. C swings low for support..."
    ],
    "primary_zone": "defensive",
    "key_concepts": ["puck movement", "support timing", "lane creation"]
  }
  ```

### 5. Map to Zone-Based Spec
- **Tool**: `map_formation_to_zones` (NEW)
- **Input**: Structured formation data
- **Output**: Complete diagram specification with all entities
  ```
  {
    "players": [
      {
        "role": "LD",
        "zone": "d-corner-left-low",
        "offset": {"x": -5, "y": 0, "description": "deep in corner"},
        "team": "home",
        "has_puck": true,
        "sequence": 1
      },
      {
        "role": "RD", 
        "zone": "d-behind-net-right",
        "offset": {"x": 0, "y": 0, "description": "standard position"},
        "team": "home",
        "has_puck": false,
        "sequence": 1
      }
    ],
    "movements": [
      {
        "from": "LD",
        "to": "RD",
        "type": "pass",
        "sequence": 1,
        "style": "dashed"
      },
      {
        "from": "C",
        "to": "d-behind-net-left",
        "type": "skating",
        "sequence": 2,
        "style": "solid"
      }
    ],
    "zones": [
      {
        "purpose": "support",
        "areas": ["d-circle-left-low", "d-circle-right-low"],
        "team": "home",
        "opacity": 0.2
      }
    ],
    "metadata": {
      "category": "play",
      "view": "defensive",
      "title": "WHEEL Breakout",
      "focus": "Controlled breakout using D-to-D pass"
    }
  }
  ```

### 6. Generate Diagram
- **Tool**: `generate_diagram_from_spec` (existing)
- **Input**: Zone-based specification
- **Output**: Diagram file path and base64 image

## Entity Decision Framework

### Player Entities
Each player requires these decisions:
- **Role**: C, RW, LW, LD, RD, G, F1-F3, D1-D2, X1-X5, XG
- **Zone**: One of 32 zones (e.g., "d-corner-left-low")
- **Offset**: Fine positioning within zone
  - Examples: "deep", "high", "near boards", "slot-side"
  - Translates to coordinate adjustments
- **Team**: home/away/practicing
- **Puck Possession**: Boolean
- **Sequence**: For multi-step drills/plays

### Movement Entities
Each movement requires:
- **Type Selection**:
  - `pass` - Puck transfer (dashed line)
  - `skating` - Player movement (solid arrow)
  - `skating_with_puck` - Puck carry (solid with puck)
  - `shot` - Shooting attempt (thick arrow)
  - `check` - Defensive pressure (curved arrow)
  - `support` - Support movement (dotted arrow)
  - `forechecking` - Offensive pressure
  - `backchecking` - Defensive recovery
- **Routing**: From player/zone to player/zone
- **Sequence**: Order of execution
- **Visual Style**: Line appearance

### Zone Coverage Entities
Each coverage zone requires:
- **Purpose**:
  - `pressure` - Forechecking area
  - `coverage` - Defensive responsibility
  - `support` - Backup positioning
  - `screening` - Lane blocking
  - `neutral_trap` - NZ clogging
  - `power_play_setup` - PP formation
  - `penalty_kill_box` - PK structure
- **Area Selection**: Which zones to highlight
- **Team Control**: home/away
- **Visual Intensity**: Opacity (0.1-0.5)

### Metadata
- **Category**: formation/drill/faceoff/play/system
- **View**: full/offensive/defensive/neutral
- **Title**: Descriptive name
- **Focus**: Primary tactical objective

## Implementation Benefits

### 1. Transparency
- Each transformation step is visible
- Easy to inspect intermediate outputs
- Clear understanding of how research becomes a diagram

### 2. Debuggability
- Can identify exactly where issues occur
- Each tool can be tested independently
- Logging at each stage for troubleshooting

### 3. Flexibility
- Can adjust zone mappings without regenerating research
- Can retry specific steps if needed
- Easy to add new offset types or movement styles

### 4. Quality Control
- Structured data at each stage ensures consistency
- LLM has clear schemas to follow
- Reduces hallucination through constrained choices

## Agent Instructions Update

The agent will be given updated instructions that explain:
1. When to use each tool (but not forced flow)
2. How outputs from one tool inform the next
3. Error handling and fallback strategies
4. Performance optimization (e.g., check presets first)

## Success Metrics

1. **Accuracy**: Diagrams match standard hockey tactics
2. **Transparency**: Can inspect all transformation stages
3. **Performance**: Fast path for known formations (<2s)
4. **Flexibility**: Can handle novel formations through research
5. **Debuggability**: Clear error messages and logging

## Next Steps

1. Implement `synthesize_research_to_formation` tool
2. Implement `map_formation_to_zones` tool with comprehensive entity mapping
3. Create detailed prompt templates for zone mapping decisions
4. Update agent instructions with new tool guidance
5. Add comprehensive logging at each stage
6. Test with known and unknown formations

This enhanced flow provides the transparency and control needed while maintaining the flexibility of the OpenAI Agents SDK architecture.