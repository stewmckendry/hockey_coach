# Update Spec with Clarifications - Design Document

## Problem Statement

After `translate_analysis_to_spec` runs, client apps need to:
1. Show questions/warnings to users
2. Collect clarifications 
3. Re-call translation with clarifications to update spec
4. Maintain conversation history across multiple LLM calls

**Challenge**: `translate_analysis_to_spec` makes 3 separate LLM calls, each with its own `response_id`:
- Player mapping: `map_positions_with_llm()` 
- Movement mapping: `map_movements_with_llm()`
- Equipment mapping: `map_equipment_with_llm()`

## Solution Architecture

### 1. Enhanced Response Tracking

Modify `translate_analysis_to_spec` to return response IDs:

```json
{
  "success": true,
  "spec": {...},
  "metadata": {...},
  "conversation": {
    "response_ids": {
      "player_mapping": "resp_abc123",
      "movement_mapping": "resp_def456", 
      "equipment_mapping": "resp_ghi789"
    },
    "note": "Use these for clarification updates"
  }
}
```

### 2. Smart Clarification Routing

Create `update_spec_with_clarifications` tool that routes clarifications based on their keys:

```python
CLARIFICATION_ROUTING = {
    # Player-related clarifications
    "point_side": "player_mapping",
    "position_*": "player_mapping",
    "handedness": "player_mapping",
    
    # Movement-related clarifications  
    "timing": "movement_mapping",
    "sequence": "movement_mapping",
    "path_*": "movement_mapping",
    
    # Equipment-related clarifications
    "equipment_placement": "equipment_mapping",
    "equipment_*": "equipment_mapping"
}
```

### 3. Enhanced Mapping Functions

Modify existing mapping functions to support clarifications:

```python
def map_positions_with_llm(
    players: List[Dict[str, Any]],
    rink_view: str = "offensive",
    clarifications: Optional[Dict[str, Any]] = None,
    previous_response_id: Optional[str] = None
) -> Dict[str, Any]:
    """Enhanced with clarification support."""
    
    # Build prompt with clarifications
    if clarifications:
        clarification_text = build_clarification_text(clarifications)
        prompt += f"\n\nUser Clarifications:\n{clarification_text}"
        prompt += "\n\nUpdate the positions based on these clarifications."
    
    # Include previous_response_id for conversation continuity
    api_request = {...}
    if previous_response_id:
        api_request["previous_response_id"] = previous_response_id
    
    response = client.responses.create(**api_request)
    
    return {
        "players_mapped": [...],
        "response_id": response.id,  # New response ID
        "clarifications_applied": clarifications or {}
    }
```

### 4. Main Update Tool

```python
@mcp.tool("update_spec_with_clarifications")
def update_spec_with_clarifications(
    original_spec: Dict[str, Any],
    clarifications: Dict[str, Any],
    conversation_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update diagram spec with user clarifications.
    Only updates components affected by clarifications.
    """
    
    # Get original response IDs
    response_ids = conversation_metadata.get("response_ids", {})
    
    # Route clarifications to appropriate components
    needs_player_update = any(
        key.startswith(("point_", "position_", "handedness"))
        for key in clarifications.keys()
    )
    needs_movement_update = any(
        key.startswith(("timing", "sequence", "path_"))
        for key in clarifications.keys()  
    )
    needs_equipment_update = any(
        key.startswith(("equipment_",))
        for key in clarifications.keys()
    )
    
    updated_spec = original_spec.copy()
    new_response_ids = response_ids.copy()
    changes_made = []
    
    # Update only affected components
    if needs_player_update:
        player_clarifications = {
            k: v for k, v in clarifications.items()
            if k.startswith(("point_", "position_", "handedness"))
        }
        
        # Reconstruct players from original analysis (stored in conversation_metadata)
        original_players = conversation_metadata.get("original_analysis", {})
                          .get("components_with_assumptions", {})
                          .get("players", [])
        
        player_result = map_positions_with_llm(
            players=original_players,
            rink_view=updated_spec["rink"]["view"],
            clarifications=player_clarifications,
            previous_response_id=response_ids.get("player_mapping")
        )
        
        updated_spec["players"] = player_result["players_mapped"]
        new_response_ids["player_mapping"] = player_result["response_id"]
        changes_made.append("Updated player positions")
    
    # Similar for movements and equipment...
    
    return {
        "success": True,
        "updated_spec": updated_spec,
        "changes_made": changes_made,
        "conversation": {
            "response_ids": new_response_ids,
            "clarifications_applied": clarifications
        },
        "remaining_questions": extract_remaining_questions(updated_spec)
    }
```

## Implementation Strategy

### Phase 1: Response ID Tracking
1. Modify `translate_analysis_to_spec` to capture and return response IDs from all 3 mapping calls
2. Store original analysis in conversation metadata for reconstruction

### Phase 2: Enhanced Mapping Functions  
1. Add `clarifications` and `previous_response_id` parameters to mapping functions
2. Update prompts to handle clarification context
3. Return new response IDs for conversation continuity

### Phase 3: Update Tool
1. Implement `update_spec_with_clarifications` with smart routing
2. Add clarification key pattern matching
3. Implement selective component updates

### Phase 4: Client Integration
1. Client stores conversation metadata from initial translation
2. Shows questions to users and collects clarifications
3. Calls update tool with clarifications + conversation metadata
4. Receives updated spec with new conversation state

## Benefits

1. **Efficient**: Only updates affected components, not entire spec
2. **Conversational**: Maintains LLM conversation context across multiple calls
3. **Modular**: Reuses existing mapping functions with enhancements
4. **Scalable**: Easy to add new clarification types and routing rules
5. **User-Friendly**: Supports iterative refinement without starting over

## Example Client Flow

```javascript
// 1. Initial translation
const initialResult = await translateAnalysisToSpec(analysis);
const { spec, metadata, conversation } = initialResult;

// 2. Show questions to user
if (metadata.critical_questions.length > 0) {
  const clarifications = await showQuestionsToUser(metadata.critical_questions);
  
  // 3. Update with clarifications
  const updateResult = await updateSpecWithClarifications(
    spec, 
    clarifications,
    { response_ids: conversation.response_ids, original_analysis: analysis }
  );
  
  // 4. Use updated spec
  const finalSpec = updateResult.updated_spec;
}
```