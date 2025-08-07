"""
Simplified hockey diagram agent that works without timing out.
"""
import asyncio
import logging
from typing import Dict, Any
from pathlib import Path

from core_tools import (
    parse_hockey_formation_core,
    generate_diagram_from_spec_core,
    list_formations_core
)

logger = logging.getLogger(__name__)

class SimpleHockeyAgent:
    """Simple agent that directly uses core tools without OpenAI SDK complexity."""
    
    async def generate_diagram(self, request: str) -> Dict[str, Any]:
        """Generate a hockey diagram from request."""
        try:
            # First try to parse the formation
            logger.info(f"Parsing request: {request}")
            parsed = await parse_hockey_formation_core(request)
            
            if not parsed['success']:
                return {
                    "success": False,
                    "error": f"Failed to parse formation: {parsed.get('error', 'Unknown error')}",
                    "response": f"❌ Could not understand the formation: {request}"
                }
            
            # Generate the diagram
            logger.info("Generating diagram from parsed data")
            diagram_result = await generate_diagram_from_spec_core(parsed['parsed_data'])
            
            if diagram_result['success']:
                response = f"""✅ Generated {request} diagram

📁 Diagram: {diagram_result['diagram_path']}

🏒 **Formation**: {request} with {len(parsed['parsed_data']['players'])} players positioned strategically.

💡 **Coaching Point**: This formation provides structured offensive/defensive coverage."""
                
                return {
                    "success": True,
                    "response": response,
                    "diagram_path": diagram_result['diagram_path'],
                    "tools_used": ["parse_hockey_formation", "generate_diagram_from_spec"]
                }
            else:
                return {
                    "success": False,
                    "error": diagram_result.get('error', 'Generation failed'),
                    "response": f"❌ Failed to generate diagram: {diagram_result.get('error', 'Unknown error')}"
                }
                
        except Exception as e:
            logger.error(f"Error in simple agent: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": f"❌ Error: {str(e)}"
            }

# Global instance
_simple_agent = None

async def get_simple_agent():
    """Get or create simple agent instance."""
    global _simple_agent
    if _simple_agent is None:
        _simple_agent = SimpleHockeyAgent()
    return _simple_agent

async def generate_with_simple_agent(request: str) -> Dict[str, Any]:
    """Generate diagram using simple agent."""
    agent = await get_simple_agent()
    return await agent.generate_diagram(request)