"""
Hockey Diagram Feedback Processor
Interprets natural language feedback to update diagram specifications
"""

import logging
import json
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from openai import OpenAI

logger = logging.getLogger(__name__)

@dataclass
class FeedbackChange:
    """Represents a single change made to the diagram spec"""
    change_type: str  # 'move', 'add', 'remove', 'modify'
    target: str       # What was changed
    details: str      # Human-readable description
    
@dataclass
class FeedbackResult:
    """Result of processing feedback"""
    updated_spec: Dict[str, Any]
    changes: List[FeedbackChange]
    explanation: str
    success: bool
    error_message: Optional[str] = None
    processing_time: float = 0.0

class FeedbackProcessor:
    """Processes natural language feedback to update hockey diagram specifications"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the feedback processor with OpenAI client"""
        self.client = OpenAI(api_key=openai_api_key) if openai_api_key else OpenAI()
        
        # Feedback interpretation prompt
        self.system_prompt = """You are a hockey diagram feedback interpreter. 
        Given a current diagram specification and natural language feedback, 
        determine what changes need to be made to the spec.
        
        Common feedback patterns:
        - Position changes: "Move X to Y" → Update player's zone/position
        - Add elements: "Add player at X" → Insert new player in spec
        - Remove elements: "Remove X" → Delete from spec
        - Add movements: "Show pass from X to Y" → Add arrow/movement
        - Modify properties: "Make X defensive" → Change team/color
        
        Hockey zones: offensive_left, offensive_slot, offensive_right, 
                     neutral_left, neutral_center, neutral_right,
                     defensive_left, defensive_slot, defensive_right,
                     behind_net, goal_line, point, high_slot, low_slot
        
        Return a JSON object with:
        {
            "changes": [
                {
                    "type": "move|add|remove|modify",
                    "target": "what to change",
                    "action": "specific change to make",
                    "details": "human-readable description"
                }
            ],
            "updated_spec": {full updated specification},
            "explanation": "Brief summary of changes made"
        }
        """
        
        # Track metrics
        self.metrics = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'average_time': 0,
            'common_patterns': {}
        }
    
    def process_feedback(self, current_spec: Dict[str, Any], feedback: str) -> FeedbackResult:
        """
        Process natural language feedback to update diagram specification
        
        Args:
            current_spec: Current diagram specification
            feedback: Natural language description of desired changes
            
        Returns:
            FeedbackResult with updated spec and change details
        """
        start_time = time.time()
        
        try:
            # Prepare the prompt
            user_prompt = f"""
            Current diagram specification:
            {json.dumps(current_spec, indent=2)}
            
            User feedback: "{feedback}"
            
            Apply the requested changes and return the updated specification.
            """
            
            # Call OpenAI to interpret feedback
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,  # Lower temperature for consistent interpretation
                    response_format={"type": "json_object"}
                )
            except Exception as api_error:
                # Fallback without response_format if not supported
                if "response_format" in str(api_error):
                    response = self.client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": self.system_prompt + "\n\nIMPORTANT: Return ONLY valid JSON, no other text."},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.3
                    )
                else:
                    raise api_error
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            
            # Validate the updated spec
            updated_spec = result.get('updated_spec', current_spec)
            if not self._validate_spec(updated_spec):
                raise ValueError("Updated specification is invalid")
            
            # Create change objects
            changes = [
                FeedbackChange(
                    change_type=change['type'],
                    target=change['target'],
                    details=change['details']
                )
                for change in result.get('changes', [])
            ]
            
            # Update metrics
            self._update_metrics(feedback, True, time.time() - start_time)
            
            return FeedbackResult(
                updated_spec=updated_spec,
                changes=changes,
                explanation=result.get('explanation', 'Changes applied'),
                success=True,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            self._update_metrics(feedback, False, time.time() - start_time)
            
            return FeedbackResult(
                updated_spec=current_spec,
                changes=[],
                explanation="",
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def _validate_spec(self, spec: Dict[str, Any]) -> bool:
        """
        Validate that a specification has required structure
        
        Args:
            spec: Specification to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check for required fields
        if 'players' not in spec:
            return False
            
        # Validate player structure - we expect zone-based specs for editing
        for player in spec.get('players', []):
            # Must have position (role identifier like 'F1', 'C', 'D1')
            if 'position' not in player:
                return False
            
            # Should have zone for semantic positioning
            # But we'll allow coordinates as fallback for backward compatibility
            has_zone = 'zone' in player
            has_coordinates = 'x' in player and 'y' in player
            
            if not (has_zone or has_coordinates):
                # Player must have either zone or coordinates
                return False
                
        # Validate movements if present
        for movement in spec.get('movements', []):
            # Movements should reference player positions
            if 'from_position' not in movement or 'to_position' not in movement:
                # Also accept legacy 'from' and 'to' fields
                if 'from' not in movement or 'to' not in movement:
                    return False
                
        return True
    
    def _update_metrics(self, feedback: str, success: bool, processing_time: float):
        """Update processing metrics for monitoring"""
        self.metrics['total_processed'] += 1
        
        if success:
            self.metrics['successful'] += 1
        else:
            self.metrics['failed'] += 1
            
        # Update average time
        current_avg = self.metrics['average_time']
        total = self.metrics['total_processed']
        self.metrics['average_time'] = (current_avg * (total - 1) + processing_time) / total
        
        # Track common feedback patterns
        feedback_lower = feedback.lower()
        if 'move' in feedback_lower:
            self.metrics['common_patterns']['move'] = self.metrics['common_patterns'].get('move', 0) + 1
        if 'add' in feedback_lower:
            self.metrics['common_patterns']['add'] = self.metrics['common_patterns'].get('add', 0) + 1
        if 'remove' in feedback_lower or 'delete' in feedback_lower:
            self.metrics['common_patterns']['remove'] = self.metrics['common_patterns'].get('remove', 0) + 1
        if 'pass' in feedback_lower or 'arrow' in feedback_lower:
            self.metrics['common_patterns']['movement'] = self.metrics['common_patterns'].get('movement', 0) + 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current processing metrics"""
        return self.metrics.copy()
    
    def suggest_improvements(self, spec: Dict[str, Any]) -> List[str]:
        """
        Suggest possible improvements or modifications for a diagram
        
        Args:
            spec: Current diagram specification
            
        Returns:
            List of suggested improvements
        """
        suggestions = []
        
        # Check for missing elements
        if not spec.get('movements'):
            suggestions.append("Add passing lanes or player movements")
            
        # Check player distribution
        player_count = len(spec.get('players', []))
        if player_count < 5:
            suggestions.append("Add more players to show full formation")
        elif player_count > 10:
            suggestions.append("Consider focusing on key players only")
            
        # Check for defensive players
        has_defense = any(p.get('team') == 'away' for p in spec.get('players', []))
        if not has_defense:
            suggestions.append("Add defensive players to show pressure")
            
        return suggestions


# Example usage and testing
if __name__ == "__main__":
    # Test the feedback processor
    processor = FeedbackProcessor()
    
    # Example spec
    test_spec = {
        "title": "Power Play Umbrella",
        "players": [
            {"position": "F1", "zone": "point", "team": "home"},
            {"position": "F2", "zone": "offensive_left", "team": "home"},
            {"position": "F3", "zone": "offensive_right", "team": "home"},
            {"position": "C", "zone": "high_slot", "team": "home"},
            {"position": "F4", "zone": "offensive_slot", "team": "home"}
        ],
        "movements": []
    }
    
    # Test feedback
    test_feedback = "Move F2 down to the goal line for a low umbrella setup"
    
    print("Testing feedback processor...")
    print(f"Feedback: {test_feedback}")
    
    result = processor.process_feedback(test_spec, test_feedback)
    
    if result.success:
        print(f"\nSuccess! Explanation: {result.explanation}")
        print(f"Changes made: {len(result.changes)}")
        for change in result.changes:
            print(f"  - {change.change_type}: {change.details}")
        print(f"Processing time: {result.processing_time:.2f}s")
    else:
        print(f"\nError: {result.error_message}")
    
    # Show metrics
    print(f"\nMetrics: {processor.get_metrics()}")
    
    # Get suggestions
    suggestions = processor.suggest_improvements(test_spec)
    print(f"\nSuggestions: {suggestions}")