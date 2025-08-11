# Hockey Diagram Interactive Editing System - Technical Design

## Overview

This document outlines the technical design and implementation plan for the interactive editing system that allows users to modify hockey diagrams using natural language feedback. The system focuses on spec-only storage for efficiency and perfect reproducibility.

## Core Principles

1. **Spec-Only Storage**: Save only diagram specifications (~1KB), not images (~100KB)
2. **Natural Language Processing**: Interpret user feedback to update specs
3. **Progressive Refinement**: Multiple iterations without starting over
4. **Perfect Reproducibility**: Generate identical diagrams from specs
5. **Seamless Integration**: Build on existing caching infrastructure

## User Journey

### Primary Flow: Post-Generation Modification

```
1. User generates diagram (new or from cache)
   ↓
2. System displays diagram with "Modify" button
   ↓
3. User clicks "Modify" and enters natural language feedback
   Example: "Move F1 to the slot" or "Add passing arrows"
   ↓
4. System processes feedback and updates spec
   ↓
5. Diagram regenerates from updated spec
   ↓
6. User can continue modifying or save to library
   ↓
7. Only spec is saved (no image files)
```

### Secondary Flow: Cache-Based Modification

```
1. User searches for similar diagram
   ↓
2. System finds semantic matches in cache
   ↓
3. User selects and modifies cached spec
   ↓
4. Progressive refinement through feedback
   ↓
5. Save as new variation or update existing
```

## Technical Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
├─────────────────────────────────────────────────────────┤
│  hockey-diagram-test/page.tsx                           │
│  - Feedback UI Component                                │
│  - Modification History Tracking                        │
│  - Spec State Management                                │
└────────────┬────────────────────────┬───────────────────┘
             │                        │
             ▼                        ▼
┌─────────────────────────┐  ┌──────────────────────────┐
│  /feedback-processor    │  │  /generate-from-spec     │
│  Process natural lang   │  │  Generate from spec only │
└────────────┬────────────┘  └────────────┬──────────────┘
             │                             │
             ▼                             ▼
┌─────────────────────────────────────────────────────────┐
│              MCP Server (FastMCP Python)                │
├─────────────────────────────────────────────────────────┤
│  process_diagram_feedback    generate_diagram_from_spec │
│  FeedbackProcessor           DiagramGenerator          │
└─────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│                  ChromaDB Cache                         │
│              (Specs Only - No Images)                   │
└─────────────────────────────────────────────────────────┘
```

## Implementation Components

### 1. Frontend Components

#### Feedback UI Component
- Textarea for natural language input
- Apply/Cancel buttons
- Modification history display
- Success/error notifications

#### State Management
```typescript
interface FeedbackState {
  feedbackMode: boolean
  feedbackText: string
  currentSpec: DiagramSpec | null
  modificationHistory: ModificationEntry[]
  isProcessing: boolean
}

interface ModificationEntry {
  feedback: string
  changes: string[]
  timestamp: Date
}
```

### 2. API Endpoints

#### `/api/hockey-diagram/feedback-processor`
- **Method**: POST
- **Input**: `{ currentSpec, feedback }`
- **Output**: `{ updatedSpec, changes, explanation }`
- **Purpose**: Process natural language to spec updates

#### `/api/hockey-diagram/generate-from-spec`
- **Method**: POST
- **Input**: `{ spec }`
- **Output**: `{ imageBase64, success }`
- **Purpose**: Generate diagram from spec only

### 3. MCP Tools

#### `process_diagram_feedback`
```python
Args:
  current_spec: Current diagram specification
  feedback: Natural language description of changes
  
Returns:
  updated_spec: Modified specification
  changes_made: List of applied changes
  explanation: Human-readable explanation
```

### 4. Feedback Processor

#### Core Logic
```python
class FeedbackProcessor:
    def process_feedback(spec, feedback):
        1. Parse current spec structure
        2. Interpret feedback using GPT-4
        3. Apply changes to spec
        4. Validate updated spec
        5. Return changes and explanation
```

#### Feedback Patterns
- **Position Changes**: "Move X to Y" → Update zone
- **Add Elements**: "Add player at X" → Insert player
- **Remove Elements**: "Remove X" → Delete from spec
- **Add Movements**: "Show pass from X to Y" → Add arrow
- **Modify Properties**: "Make X defensive" → Change team

### 5. Spec Storage

#### Current Structure (No Changes Needed)
```python
{
  'id': 'diagram_xxx',
  'prompt': 'Original request',
  'spec': {
    'title': 'Formation name',
    'players': [...],
    'movements': [...],
    'zones': [...]
  },
  'metadata': {
    'created_at': '2024-01-20T10:00:00',
    'modified_at': '2024-01-20T10:30:00',
    'modification_count': 3,
    'tags': ['powerplay', 'refined']
  }
}
```

## Implementation Plan

### Phase 1: Core Feedback System (Week 1)

- [ ] Create `feedback_processor.py` module
- [ ] Implement `process_diagram_feedback` MCP tool
- [ ] Create `/feedback-processor` API endpoint
- [ ] Design GPT-4 prompts for feedback interpretation
- [ ] Add feedback validation logic
- [ ] Write unit tests for feedback processor

### Phase 2: Frontend Integration (Week 1-2)

- [ ] Add feedback UI component to test page
- [ ] Implement state management for modifications
- [ ] Create modification history tracking
- [ ] Add feedback submission logic
- [ ] Implement spec update handling
- [ ] Add success/error notifications
- [ ] Create loading states

### Phase 3: Generate-from-Spec Endpoint (Week 2)

- [ ] Create `/generate-from-spec` API endpoint
- [ ] Add base64 image reading utility
- [ ] Implement error handling
- [ ] Add response caching for identical specs
- [ ] Write integration tests

### Phase 4: Enhanced Features (Week 2-3)

- [ ] Add undo/redo functionality
- [ ] Implement spec diff visualization
- [ ] Create feedback suggestions/autocomplete
- [ ] Add batch modification support
- [ ] Implement spec versioning
- [ ] Add modification analytics

### Phase 5: Testing & Polish (Week 3)

- [ ] Comprehensive testing of feedback patterns
- [ ] Performance optimization
- [ ] Error message improvements
- [ ] Documentation updates
- [ ] User guide creation
- [ ] Example library of modifications

## Feedback Processing Examples

### Example 1: Position Change
```
Input: "Move the center to the low slot"
Current Spec: { position: "C", zone: "high_slot" }
Updated Spec: { position: "C", zone: "low_slot" }
Explanation: "Moved center from high slot to low slot"
```

### Example 2: Add Movement
```
Input: "Add a pass from D1 to D2"
Current Spec: { movements: [] }
Updated Spec: { movements: [{ from: "D1", to: "D2", type: "pass" }] }
Explanation: "Added passing movement from D1 to D2"
```

### Example 3: Complex Change
```
Input: "Show forechecking pressure with F1 and F2 in offensive zone"
Current Spec: { players: [...home team...] }
Updated Spec: { 
  players: [
    ...home team...,
    { position: "F1", zone: "offensive_slot", team: "away" },
    { position: "F2", zone: "offensive_left", team: "away" }
  ]
}
Explanation: "Added 2 forecheckers (F1, F2) in offensive zone"
```

## Success Metrics

- **Feedback Processing Accuracy**: >90% correct interpretation
- **Processing Time**: <2 seconds per feedback
- **User Iterations**: Average 3-5 refinements per session
- **Spec Storage Savings**: 99% reduction vs image storage
- **Cache Hit Rate**: >70% for similar diagrams

## Error Handling

### Feedback Processing Errors
- Invalid feedback → Suggest alternatives
- Ambiguous requests → Ask for clarification
- Conflicting changes → Show options
- Spec validation failures → Detailed error messages

### System Errors
- API failures → Retry with exponential backoff
- OpenAI rate limits → Queue and retry
- Cache failures → Fallback to direct generation
- Network issues → Offline mode with local storage

## Security Considerations

- Sanitize natural language input
- Validate spec structure before saving
- Rate limit feedback requests
- Audit log all modifications
- Implement user quotas for API usage

## Future Enhancements

1. **AI-Powered Suggestions**: Proactive improvement recommendations
2. **Voice Input**: Speech-to-text for feedback
3. **Collaborative Editing**: Real-time multi-user modifications
4. **Template Library**: Common modification patterns
5. **Visual Diff Tool**: Side-by-side spec comparisons
6. **Export Options**: Generate coaching documentation from specs

## Dependencies

- OpenAI GPT-4 API for feedback processing
- Existing ChromaDB cache infrastructure
- Current MCP server and tools
- Next.js frontend framework
- FastMCP for tool implementation

## Conclusion

This interactive editing system provides a powerful, efficient way for users to refine hockey diagrams through natural language. By focusing on spec-only storage and leveraging AI for feedback interpretation, we achieve both storage efficiency and perfect reproducibility while maintaining an intuitive user experience.