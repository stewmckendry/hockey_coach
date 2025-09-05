"""
Agent Trace Logger - Captures the hockey-diagram-expert agent's decision process.
Logs each step, tool use, and thought process for retrospective analysis.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class AgentTraceLogger:
    """Logger for tracking agent decisions and actions."""
    
    def __init__(self, spreadsheet_id: str = "1_RdgMPxluftZfeFl1SXZKYycDVxAV-GrzzhESIOXt24"):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = "Agent_Trace_Log"
        self.session_id = str(uuid.uuid4())[:8]  # Short session ID
        self.step_count = 0
        self.drill_request = ""
        self.trace_buffer = []  # Buffer traces before writing
        
    def start_session(self, drill_request: str):
        """Initialize a new trace session."""
        self.drill_request = drill_request
        self.step_count = 0
        self.trace_buffer = []
        
        # Log the initial request
        self.log_step(
            phase="1_Discovery",
            action="parse_request",
            thought="Understanding the drill requirements",
            input_data=drill_request,
            output="Parsed drill components"
        )
        
    def log_step(self, 
                 phase: str,
                 action: str,
                 thought: str,
                 input_data: Any = "",
                 output: str = "",
                 issues: List[str] = None):
        """Log a single step in the agent's process."""
        self.step_count += 1
        
        trace_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'drill_request': self.drill_request[:100],  # Truncate long requests
            'step_number': self.step_count,
            'phase': phase,
            'action': action,
            'thought': thought,
            'input': str(input_data)[:200] if input_data else "",  # Truncate
            'output_summary': output[:200] if output else "",  # Truncate
            'issues_found': ", ".join(issues) if issues else ""
        }
        
        self.trace_buffer.append(trace_entry)
        
    def log_analysis(self, analysis_result: Dict):
        """Log the drill analysis phase."""
        self.log_step(
            phase="1.5_Analysis",
            action="analyze_drill",
            thought="Completing mandatory drill analysis framework",
            input_data=self.drill_request,
            output=f"Zones: {analysis_result.get('zones_required', [])}; Players: {len(analysis_result.get('players', []))}"
        )
        
    def log_template_search(self, templates_found: List[Dict]):
        """Log template discovery."""
        if templates_found:
            best_match = templates_found[0]
            self.log_step(
                phase="2_Schema",
                action="find_drill_template",
                thought=f"Found matching template: {best_match['name']}",
                input_data=self.drill_request,
                output=f"{best_match['confidence']:.0%} confidence match"
            )
        else:
            self.log_step(
                phase="2_Schema",
                action="find_drill_template",
                thought="No matching templates found, building from scratch",
                input_data=self.drill_request,
                output="No templates"
            )
            
    def log_validation(self, spatial_issues: List[str], diagram_issues: List[str]):
        """Log validation results."""
        all_issues = spatial_issues + diagram_issues
        self.log_step(
            phase="5_Validation",
            action="validate_spatial_placement",
            thought="Checking for collisions and placement issues",
            input_data="DiagramSpec",
            output=f"{len(all_issues)} issues found",
            issues=all_issues[:5]  # Log first 5 issues
        )
        
    def log_iteration(self, feedback: str, changes_made: str):
        """Log an iteration based on user feedback."""
        self.log_step(
            phase="6_Iteration",
            action="apply_feedback",
            thought="Adjusting diagram based on user feedback",
            input_data=feedback,
            output=changes_made
        )
        
    def complete_session(self, success: bool, lessons: str = ""):
        """Mark session complete and write to sheet."""
        # Add final summary
        final_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'drill_request': self.drill_request[:100],
            'step_number': 'FINAL',
            'phase': '7_Complete',
            'action': 'session_complete',
            'thought': 'Session completed',
            'input': '',
            'output_summary': 'Success' if success else 'Failed',
            'issues_found': '',
            'final_success': 'TRUE' if success else 'FALSE',
            'lessons_learned': lessons
        }
        
        # Write all entries to Google Sheets
        self._write_to_sheets()
        
    def get_sheet_rows(self):
        """Get formatted rows ready for Google Sheets."""
        rows = []
        for entry in self.trace_buffer:
            row = [
                entry.get('timestamp', ''),
                entry.get('session_id', ''),
                entry.get('drill_request', ''),
                str(entry.get('step_number', '')),
                entry.get('phase', ''),
                entry.get('action', ''),
                entry.get('thought', ''),
                entry.get('input', ''),
                entry.get('output_summary', ''),
                entry.get('issues_found', ''),
                entry.get('final_success', ''),
                entry.get('lessons_learned', '')
            ]
            rows.append(row)
        return rows
    
    def _write_to_sheets(self):
        """Note: Agent should call get_sheet_rows() and use mcp__google-sheets tools."""
        # Save local backup
        trace_file = f"manual_diagrams/logs/trace_{self.session_id}.json"
        os.makedirs(os.path.dirname(trace_file), exist_ok=True)
        with open(trace_file, 'w') as f:
            json.dump(self.trace_buffer, f, indent=2)
        
        print(f"Trace saved locally to {trace_file}")
        print(f"Agent should write {len(self.trace_buffer)} rows to Google Sheets")
        
        
# Convenience functions for agent

def start_trace(drill_request: str) -> AgentTraceLogger:
    """Start a new trace session."""
    logger = AgentTraceLogger()
    logger.start_session(drill_request)
    return logger


def log_agent_thought(logger: AgentTraceLogger, phase: str, action: str, thought: str):
    """Quick logging of agent thoughts."""
    logger.log_step(phase=phase, action=action, thought=thought)


# Example usage in agent:
"""
from agent_trace_logger import start_trace, log_agent_thought

# At start of diagram creation
logger = start_trace(description)

# During analysis
log_agent_thought(logger, "1.5_Analysis", "identify_zones", 
                 "Drill uses opposite circles - checking if same zone or different zones")

# After template search
logger.log_template_search(templates)

# After validation
logger.log_validation(spatial_issues, diagram_issues)

# At completion
logger.complete_session(success=True, lessons="Cross-ice means same zone, not opposite zones")
"""