# Hockey Diagram Interactive Editing Feature

## Overview
The Interactive Editing feature allows users to modify generated hockey diagrams using natural language feedback. This creates an iterative refinement workflow where coaches can progressively adjust tactical diagrams until they perfectly represent their intended play.

## Architecture

### Core Components

1. **Feedback Processor** (`servers/hockey_diagram_mcp/feedback_processor.py`)
   - Natural language understanding for diagram modifications
   - Intelligent spec updates based on user intent
   - Zone-based positioning system

2. **MCP Tool** (`process_diagram_feedback`)
   - Exposed via FastMCP decorator
   - Processes feedback and returns updated specifications
   - Maintains semantic zone structure

3. **API Endpoints**
   - `/api/hockey-diagram/feedback-processor` - Processes natural language feedback
   - `/api/hockey-diagram/generate-from-spec` - Generates diagrams from specifications

4. **Frontend UI** (`web_app/app/hockey-diagram-test/page.tsx`)
   - Interactive feedback interface
   - Modification history display
   - Real-time diagram updates

## Zone-Based Specification Model

The system uses semantic zones instead of coordinates:
- **Offensive Zone**: Behind net, slot, point, half-wall, etc.
- **Defensive Zone**: Crease, corners, blue line positions
- **Neutral Zone**: Center ice, boards, between blue lines

See `servers/hockey_diagram_mcp/SPEC_MODEL.md` for complete documentation.

## Workflow

1. **Initial Generation**: User describes formation in natural language
2. **Diagram Display**: System generates and displays tactical diagram
3. **Feedback Mode**: User enters modification requests
4. **Processing**: System interprets feedback and updates spec
5. **Regeneration**: New diagram generated from updated spec
6. **History**: Modifications tracked and displayed

## Example Usage

### Initial Prompt
```
"2-1-2 forecheck with F1 pressuring behind the net"
```

### Feedback Examples
- "Move F1 to the slot"
- "Add passing lanes between defensemen"
- "Make F2 more aggressive on the boards"
- "Remove the center from neutral zone"

### Spec Structure
```json
{
  "players": [
    {
      "id": "F1",
      "team": "offense",
      "zone": "offensive",
      "position": "behind_net",
      "label": "F1"
    }
  ],
  "movements": [
    {
      "type": "pass",
      "from_player": "D1",
      "to_player": "D2"
    }
  ],
  "annotations": [],
  "zones": ["offensive"],
  "rink_view": "full"
}
```

## Technical Implementation

### Feedback Processing Pipeline
1. Parse natural language input
2. Extract intent (move, add, remove, modify)
3. Identify target entities (players, movements)
4. Apply changes to specification
5. Validate updated specification
6. Return with explanation

### API Integration
- Frontend sends current spec + feedback
- MCP tool processes and returns updated spec
- Frontend calls generate-from-spec endpoint
- New diagram displayed with modification history

## Key Features

- **Natural Language Understanding**: Interprets coaching terminology
- **Zone-Based Positioning**: Uses hockey-specific zones, not coordinates
- **Iterative Refinement**: Multiple rounds of modifications supported
- **History Tracking**: All modifications logged and displayed
- **Error Recovery**: Graceful handling of invalid requests

## Testing

Comprehensive test coverage includes:
- `test_feedback.py` - Feedback processor unit tests
- `test_interactive_editing.py` - End-to-end workflow tests
- `test_spec_validation.py` - Specification validation tests

## Performance

- Feedback processing: ~500ms average
- Diagram regeneration: ~1-2 seconds
- Total iteration cycle: ~2-3 seconds

## Future Enhancements

1. **Voice Input**: Support voice commands for hands-free editing
2. **Undo/Redo**: Navigation through modification history
3. **Templates**: Save and reuse common modifications
4. **Batch Operations**: Apply multiple changes simultaneously
5. **AI Suggestions**: Proactive improvement recommendations

## Integration with Caching

Modified diagrams can be saved to cache with modification metadata, allowing:
- Tracking of diagram evolution
- Popular modification patterns analysis
- Community sharing of refined diagrams

## Conclusion

The Interactive Editing feature transforms static diagram generation into a dynamic, collaborative process. Coaches can now iteratively refine tactical diagrams using natural language, making the tool more intuitive and powerful for real-world coaching scenarios.

## Implementation Date
January 11, 2025

## Related Issues
- Issue #101: Hockey Diagram Caching and Interactive Editing