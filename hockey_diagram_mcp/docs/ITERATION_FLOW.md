# Hockey Diagram Iteration Flow

## Overview
This document describes the iterative process for creating hockey diagrams through natural language descriptions, building a comprehensive specification through real-world coaching needs.

## Flow Process

### Step A: User Provides Description
**User (Coach)** provides a natural language description of the hockey diagram they need.

Examples:
- "Show a 2-1-2 forecheck with F1 pressuring the puck carrier"
- "Create a power play umbrella setup with movement options"
- "Draw a neutral zone regroup with D-to-D pass"

### Step B: Claude Analyzes and Builds
**Claude Code** performs the following:

1. **Analyze the description** using LLM capabilities to understand:
   - Formation type
   - Player positions
   - Movement patterns
   - Coaching intent

2. **Translate to specification** creating a JSON spec that includes:
   - Rink view configuration
   - Player objects with positions
   - Movement objects with types
   - Zones and annotations

3. **Check spec compatibility**:
   - If request fits current spec → Generate diagram
   - If request needs new features → Update spec first, then generate

4. **Build the diagram** using `diagram_builder.py`:
   ```python
   spec = DiagramSpec(...)
   builder = DiagramBuilder()
   output_path = f"outputs/diagram_{timestamp}.png"
   builder.build(spec, output_path)
   ```

### Step C: Claude Shares Results
**Claude** provides:
- **Filepath**: `/Users/.../hockey_diagram_mcp/outputs/diagram_YYYYMMDD_HHMMSS.png`
- **Spec summary**: Key elements used (players, movements, zones)
- **New features added** (if spec was updated)

Example response:
```
Generated diagram: outputs/diagram_20250127_143022.png

Spec summary:
- View: offensive zone
- Players: 5 forwards, 2 defense
- Movements: 3 passes, 2 skating patterns
- New feature: Added "drop_pass" movement type
```

### Step D: User Reviews and Provides Feedback
**User** reviews the diagram and provides feedback:
- "Move F1 closer to the boards"
- "Add defensive pressure from X1"
- "Make the pass from D1 to F2 a saucer pass"
- "Looks good!" (approval)

### Repeat B-D Until Approved
Continue iterating through steps B-D until user confirms diagram meets their needs.

### Step E: Update Tracking Sheet
**Claude** updates Google Sheets with:
- Test case description
- Final spec used
- Number of iterations
- Feedback received
- Lessons learned

## Spec Evolution Process

When a request requires new capabilities:

1. **Identify Gap**: Determine what the current spec lacks
2. **Update Spec**: Add new elements to `spec/hockey_diagram_spec.md`
3. **Update Builder**: Enhance `src/diagram_builder.py` to handle new elements
4. **Document Change**: Note the evolution in spec version history
5. **Test**: Generate diagram with new capability
6. **Track**: Record in Google Sheets for retrospective

## File Organization

```
hockey_diagram_mcp/
├── spec/
│   └── hockey_diagram_spec.md      # Living specification
├── src/
│   └── diagram_builder.py          # Builder implementation
├── outputs/
│   └── diagram_*.png               # Generated diagrams
├── docs/
│   └── ITERATION_FLOW.md          # This document
└── tracking/
    └── iterations_sheet_link.txt   # Link to Google Sheets
```

## Key Principles

1. **Spec-Driven**: Every diagram element must be in the specification
2. **Evolution Through Use**: Spec grows from real coaching needs, not speculation
3. **Hockey Canada Standards**: Follow template legend for consistency
4. **Traceable**: Every iteration is tracked for learning
5. **Coach-Friendly**: Natural language in, tactical diagram out

## Success Metrics

- Reducing iterations needed per diagram
- Growing library of reusable formations
- Spec coverage of common coaching scenarios
- Time from description to approved diagram