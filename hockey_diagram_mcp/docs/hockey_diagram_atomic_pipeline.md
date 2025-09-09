# Hockey Diagram Atomic Pipeline
## Building Confidence Through Atomic Steps

## Core Philosophy
Each atomic step should:
- Do ONE thing well
- Be independently testable
- Build confidence through validation
- Allow for correction before proceeding

## Detailed Pipeline

### Stage 0: User Input
```
"2v1 rush"
```

### Stage 1: Query Analysis & Gap Filling
**Purpose**: Identify what's missing and make smart assumptions

#### 1a. Analyze Gaps
**Tool**: `analyze_query_gaps`
```json
{
  "explicit": {
    "player_notation": "2v1",
    "drill_type": "rush"
  },
  "missing": {
    "starting_zone": null,
    "ending_zone": null,
    "rink_view": null,
    "goalie_visible": null,
    "player_positions": null,
    "movement_pattern": null,
    "pass_sequence": null,
    "shot_included": null
  },
  "questions": [
    "Where does the rush start? (neutral zone typical)",
    "Should we show the full rink or just offensive zone?",
    "Include goalie in diagram?",
    "Standard rush pattern or specific route?",
    "Does it end with a shot on goal?"
  ]
}
```

#### 1b. Generate Assumptions
**Tool**: `generate_assumptions`
```json
{
  "assumptions": {
    "starting_zone": "neutral zone (standard for rushes)",
    "ending_zone": "offensive zone",
    "rink_view": "full (to show rush development)",
    "goalie_visible": true,
    "movement_pattern": "standard 2v1 triangle",
    "includes_pass": true,
    "ends_with_shot": true
  },
  "enriched_query": "2v1 rush from neutral zone to offensive zone with triangle formation, pass, and shot on goal. Full rink view with goalie."
}
```

#### 1c. Confirm with User (Optional)
**Tool**: `confirm_assumptions`
```
Based on "2v1 rush", I'm assuming:
- Starts in neutral zone
- Full rink view
- Includes pass and shot
- Shows goalie

Proceed? (Y/n)
```

---

### Stage 2: Player Positions (Atomic Steps)

#### 2a. Extract Positions (LLM)
**Tool**: `extract_player_positions`
```json
Input: "2v1 rush with 2 forwards vs 1 defenseman"
Output: {
  "players": [
    {"id": "F1", "role": "left_forward", "team": "home", "position_description": "left side center ice"},
    {"id": "F2", "role": "right_forward", "team": "home", "position_description": "right side center ice"},
    {"id": "D1", "role": "defenseman", "team": "away", "position_description": "offensive blue line center"},
    {"id": "G1", "role": "goalie", "team": "away", "position_description": "in net"}
  ]
}
```

#### 2b. Map Positions to Coordinates
**Tool**: `map_positions_to_coordinates`
```json
Input: Position descriptions from 2a
Output: {
  "F1": {"x": 0, "y": 15, "confidence": 0.95},
  "F2": {"x": 0, "y": -15, "confidence": 0.95},
  "D1": {"x": 30, "y": 0, "confidence": 0.90},
  "G1": {"x": 89, "y": 0, "confidence": 1.0}
}
```

#### 2c. Create Position Spec
**Tool**: `create_position_spec`
```json
{
  "players": [
    {
      "id": "F1",
      "type": "forward",
      "team": "home",
      "coordinates": {"x": 0, "y": 15},
      "label": "F1"
    },
    {
      "id": "F2",
      "type": "forward", 
      "team": "home",
      "coordinates": {"x": 0, "y": -15},
      "label": "F2"
    },
    {
      "id": "D1",
      "type": "defense",
      "team": "away",
      "coordinates": {"x": 30, "y": 0},
      "label": "D1"
    },
    {
      "id": "G1",
      "type": "goalie",
      "team": "away",
      "coordinates": {"x": 89, "y": 0},
      "label": "G"
    }
  ]
}
```

#### 2d. Validate Position Spec
**Tool**: `validate_position_spec`
```json
{
  "valid": true,
  "checks": {
    "no_overlaps": "✓ Pass",
    "in_bounds": "✓ Pass",
    "hockey_logic": "✓ Pass - Valid 2v1 formation",
    "spacing": "✓ Pass - Realistic player spacing"
  }
}
```

#### 2e. Preview Positions
**Tool**: `preview_positions`
```
   POSITIONS ONLY
   ==============
   
   Neutral Zone        Offensive Zone
        |                    |
   F1   |                    |    
        |              D1    |    G
   F2   |                    |    
        |                    |
        
   ✓ F1 at center ice left
   ✓ F2 at center ice right  
   ✓ D1 at offensive blue line
   ✓ G in net
```

---

### Stage 3: Movements (Atomic Steps)

#### 3a. Extract Movements (LLM)
**Tool**: `extract_movements`
```json
Input: "2v1 rush with pass and shot" + position_spec
Output: {
  "movements": [
    {"description": "F1 rushes toward left slot"},
    {"description": "F2 rushes toward right slot"},
    {"description": "F1 passes to F2 at hash marks"},
    {"description": "F2 shoots on goal"},
    {"description": "D1 backpedals to defend"}
  ]
}
```

#### 3b. Map Movements to Coordinates
**Tool**: `map_movements_to_coordinates`
```json
Input: Movement descriptions + position_spec
Output: {
  "movements": [
    {
      "id": "m1",
      "type": "skate",
      "from": {"x": 0, "y": 15},
      "to": {"x": 75, "y": 20},
      "player": "F1"
    },
    {
      "id": "m2", 
      "type": "skate",
      "from": {"x": 0, "y": -15},
      "to": {"x": 75, "y": -20},
      "player": "F2"
    },
    {
      "id": "m3",
      "type": "pass",
      "from": {"x": 69, "y": 20},
      "to": {"x": 69, "y": -20},
      "timing": "at_hashmarks"
    },
    {
      "id": "m4",
      "type": "shot",
      "from": {"x": 75, "y": -20},
      "to": {"x": 89, "y": 0}
    },
    {
      "id": "m5",
      "type": "skate",
      "from": {"x": 30, "y": 0},
      "to": {"x": 60, "y": 0},
      "player": "D1",
      "style": "backward"
    }
  ]
}
```

#### 3c. Create Movement Spec
**Tool**: `create_movement_spec`
```json
{
  "movements": [
    {
      "type": "skate",
      "from_pos": {"x": 0, "y": 15},
      "to_pos": {"x": 75, "y": 20},
      "style": "solid",
      "label": "Rush",
      "waypoints": [[25, 17], [50, 19]]
    },
    // ... other movements
  ]
}
```

#### 3d. Validate Movement Spec
**Tool**: `validate_movement_spec`
```json
{
  "valid": true,
  "checks": {
    "paths_clear": "✓ Pass",
    "hockey_logic": "✓ Pass - Realistic rush pattern",
    "timing_sequence": "✓ Pass - Movements in logical order"
  }
}
```

#### 3e. Preview Movements
**Tool**: `preview_movements`
```
   MOVEMENTS OVERLAY
   =================
   
   F1 ----→----→---- ●
                    ↓ (pass)
   F2 ----→----→---- ● ---→ G (shot)
   
         D1 ←---←---
         (backpedal)
   
   ✓ Rush lanes established
   ✓ Pass at hash marks
   ✓ Shot on goal
```

---

### Stage 4: Additional Elements (Atomic Steps)

#### 4a. Extract Additional Info (LLM)
**Tool**: `extract_additional_elements`
```json
Input: Context from previous stages
Output: {
  "rink_view": "full",
  "equipment": ["pucks"],
  "zones": ["highlight_rush_lanes"],
  "annotations": ["2v1 Rush Drill", "Focus: Timing and passing"]
}
```

#### 4b-4e. (Similar atomic steps for each element type)

---

### Stage 5: Final Assembly

#### 5a. Assemble Full Spec
**Tool**: `assemble_full_spec`
```json
{
  "rink": {"view": "full"},
  "players": [...],  // From stage 2
  "movements": [...], // From stage 3
  "equipment": [...], // From stage 4
  "zones": [...],     // From stage 4
  "annotations": [...] // From stage 4
}
```

#### 5b. Validate Full Spec
**Tool**: `validate_full_spec`
```json
{
  "valid": true,
  "components_validated": {
    "players": "✓",
    "movements": "✓",
    "spatial_conflicts": "✓",
    "hockey_sense": "✓"
  }
}
```

#### 5c. Preview Full Diagram
**Tool**: `preview_full_diagram`
```
   COMPLETE DIAGRAM PREVIEW
   ========================
   
   [ASCII representation of full diagram]
   
   Components:
   ✓ 4 players positioned
   ✓ 5 movements defined
   ✓ Full rink view
   ✓ Annotations added
```

---

### Stage 6: Generate Final Output
**Tool**: `generate_diagram`
```json
{
  "status": "success",
  "outputs": {
    "svg": "outputs/2v1_rush_20240903.svg",
    "png": "outputs/2v1_rush_20240903.png",
    "json": "outputs/2v1_rush_20240903.json"
  }
}
```

## MCP Tools Summary

### Analysis Tools (No LLM)
1. `analyze_query_gaps` - Identify missing information
2. `generate_assumptions` - Create smart defaults

### Extraction Tools (LLM)
3. `extract_player_positions` - Get player positions
4. `extract_movements` - Get movement patterns
5. `extract_additional_elements` - Get rink view, equipment, etc.

### Mapping Tools (No LLM)
6. `map_positions_to_coordinates` - Convert descriptions to coordinates
7. `map_movements_to_coordinates` - Convert movement descriptions to paths

### Spec Creation Tools (No LLM)
8. `create_position_spec` - Build player specification
9. `create_movement_spec` - Build movement specification
10. `create_additional_spec` - Build additional elements spec

### Validation Tools (No LLM)
11. `validate_position_spec` - Check player positions
12. `validate_movement_spec` - Check movements
13. `validate_full_spec` - Check complete diagram

### Preview Tools (No LLM)
14. `preview_positions` - Show player positions
15. `preview_movements` - Show movement overlay
16. `preview_full_diagram` - Show complete diagram

### Generation Tools (No LLM)
17. `assemble_full_spec` - Combine all specs
18. `generate_diagram` - Create final output

## Why This Atomic Approach Works

### 1. **Confidence at Each Step**
- Each atomic operation is simple and verifiable
- Validation after each step catches errors early
- Preview provides visual confirmation

### 2. **Manageable Complexity**
- No single step tries to do too much
- LLM calls are focused and structured
- Deterministic steps don't rely on AI interpretation

### 3. **Error Recovery**
- Can retry individual steps without starting over
- Clear indication of where failures occur
- Easy to debug and fix specific issues

### 4. **Progressive Enhancement**
- Start with positions (foundation)
- Add movements (dynamics)
- Layer on additional elements (polish)
- Each layer builds on validated previous work

### 5. **Agent-Friendly**
- Clear success/failure signals
- Atomic steps are easy to orchestrate
- Natural checkpoints for user interaction

## Implementation Strategy

### Phase 1: Core Pipeline (Week 1)
- Build gap analysis and assumption tools
- Create position extraction and mapping
- Implement position validation and preview

### Phase 2: Movement Layer (Week 2)
- Add movement extraction and mapping
- Implement movement validation
- Create movement preview overlay

### Phase 3: Polish Layer (Week 3)
- Add additional elements extraction
- Complete full spec assembly
- Implement comprehensive validation

### Phase 4: Testing & Refinement (Week 4)
- Test with common drill patterns
- Optimize LLM prompts for reliability
- Fine-tune coordinate mappings

## Example: Complete Flow for "2v1 rush"

1. **Gap Analysis**: Identifies need for zones, view, shot
2. **Assumptions**: Neutral start, full view, includes shot
3. **Extract Positions**: F1, F2 at center, D1 at blue line
4. **Map Positions**: Exact coordinates assigned
5. **Validate Positions**: ✓ Pass
6. **Preview Positions**: Visual confirmation
7. **Extract Movements**: Rush, pass, shot patterns
8. **Map Movements**: Paths with waypoints
9. **Validate Movements**: ✓ Pass
10. **Preview Movements**: Visual confirmation
11. **Extract Additional**: Full rink, pucks, annotations
12. **Assemble Spec**: Combine all components
13. **Validate Full**: ✓ Pass
14. **Preview Full**: Complete diagram check
15. **Generate**: Final SVG/PNG output

## Conclusion

This atomic pipeline provides:
- **Predictability** through simple, focused steps
- **Reliability** through validation at each stage
- **Debuggability** through clear failure points
- **Flexibility** to adjust individual components
- **Confidence** through progressive validation

Each tool does ONE thing well, making the entire system robust and maintainable.