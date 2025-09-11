#!/usr/bin/env python3
"""
Hockey Practice Planning MCP Prompt Library Server

This MCP server provides reusable prompts for hockey practice planning and 
team management workflows. The prompts are stored as markdown files and 
returned as text for the LLM to execute with access to MCP tools.

Available MCP tools that prompts can reference:
- Airtable MCP: For practice data management
- Hockey MCP: For drill searches  
- Hockey Diagram MCP: For visual representations
- Notion MCP: For documentation export
"""

import sys
import logging
from pathlib import Path

# Add parent path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from mcp.server.fastmcp import FastMCP

# Setup logging - write to stderr to avoid interfering with stdio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Hockey Practice Planning Prompts")

# Path to prompts directory
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(filename: str) -> str:
    """Load a prompt from a markdown file."""
    filepath = PROMPTS_DIR / filename
    if not filepath.exists():
        logger.error(f"Prompt file not found: {filepath}")
        return f"Error: Prompt file '{filename}' not found"
    
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading prompt {filename}: {e}")
        return f"Error loading prompt: {e}"


# ========== PROMPT: Plan Next Practice ==========

@mcp.prompt(
    name="plan_next_practice",
    title="Plan Next Practice",
    description="Interactive workflow to generate a comprehensive practice plan based on previous feedback, skill coverage, and coach input"
)
async def plan_next_practice() -> str:
    """
    Returns the practice planning workflow prompt.
    
    The prompt guides through:
    1. Review previous practice & get coach input
    2. Analyze skill coverage (never/not recently/recently practiced)
    3. Smart drill selection with efficiency grouping
    4. Generate practice plan using template
    5. Update records in Airtable and Notion
    """
    return load_prompt("plan_next_practice.md")


# ========== PROMPT: Post-Practice Review ==========

@mcp.prompt(
    name="post_practice_review",
    title="Post-Practice Review",
    description="Capture practice outcomes, rate drills, and prepare for next practice with automatic tracking updates"
)
async def post_practice_review() -> str:
    """
    Returns the post-practice review workflow prompt.
    
    The prompt guides through:
    1. Create practice session log with coach feedback
    2. Rate drills used (effectiveness, keep/modify/drop)
    3. Verify automatic updates via table relationships
    4. Generate summary for next practice
    """
    return load_prompt("post_practice_review.md")


# ========== PROMPT: Practice Template ==========

@mcp.prompt(
    name="practice_template",
    title="Practice Plan Template",
    description="Get the standard practice plan template structure for manual planning"
)
async def practice_template() -> str:
    """
    Returns a standard practice plan template.
    
    Provides a structured template that coaches can customize
    for their specific practice needs.
    """
    return load_prompt("practice_template.md")


# ========== PROMPT: List Hockey Skills ==========

@mcp.prompt(
    name="list_hockey_skills",
    title="List Hockey Skills by Age Group",
    description="Get a categorized list of all hockey skills for tracking and planning by age group"
)
async def list_hockey_skills() -> str:
    """
    Returns a categorized list of hockey skills.
    
    Skills are organized by category and age group appropriateness
    to help with practice planning and skill tracking.
    """
    return load_prompt("hockey_skills_list.md")


# ========== PROMPT: Quick Drill Search ==========

@mcp.prompt(
    name="quick_drill_search",
    title="Quick Drill Search",
    description="Search for drills by skill focus, age group, or equipment needs"
)
async def quick_drill_search() -> str:
    """
    Returns a prompt for searching hockey drills.
    
    Guides the use of the search_hockey_drills tool
    with appropriate filters and parameters.
    """
    return load_prompt("drill_search.md")


# ========== Main Entry Point ==========

if __name__ == "__main__":
    import os
    
    logger.info("🏒 Starting Hockey Practice Planning Prompts MCP Server...")
    logger.info("Available prompts:")
    logger.info("  - plan_next_practice: Interactive practice planning workflow")
    logger.info("  - post_practice_review: Post-practice review and updates")
    logger.info("  - practice_template: Get practice plan template")
    logger.info("  - list_hockey_skills: List skills by age group")
    logger.info("  - quick_drill_search: Search for drills")
    
    # Use stdio transport for Claude Code CLI
    transport = os.getenv('MCP_TRANSPORT', 'stdio')
    
    if transport == 'stdio':
        logger.info("Starting STDIO transport for Claude Code CLI")
        mcp.run(transport="stdio")
    else:
        logger.error(f"Unsupported transport: {transport}")