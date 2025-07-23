from __future__ import annotations

"""Enhanced MCP server for comprehensive hockey coaching knowledge base."""

from typing import List, Optional, Dict, Any, Union
from typing_extensions import TypedDict
from pydantic import BaseModel
import json
import logging
from openai import OpenAI
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from mcp.server.fastmcp import FastMCP

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.chroma_utils import get_chroma_collection

mcp = FastMCP("Enhanced Hockey MCP Server")
collection = get_chroma_collection()
client = OpenAI()

# Enhanced result types with consistent structure
class HockeyKnowledgeResult(TypedDict):
    """Base structure for all hockey knowledge results."""
    id: str
    title: str
    content_type: str  # drill, video, skill, tactic, rule, dryland
    summary: str
    complexity: str
    source: str
    age_recommendation: Optional[str]
    equipment: Optional[str]
    teaching_points: Optional[str]
    skills_practiced: Optional[str]
    positions: Optional[str]
    url: Optional[str]
    metadata: Dict[str, Any]

class CoachingPlan(BaseModel):
    """Structure for generated coaching plans."""
    title: str
    age_group: str
    duration_minutes: int
    focus_areas: List[str]
    warmup: List[Dict[str, str]]
    main_activities: List[Dict[str, str]]
    cooldown: List[Dict[str, str]]
    equipment_needed: List[str]
    coaching_notes: str

class PlayerDevelopmentPlan(BaseModel):
    """Structure for individual player development."""
    player_name: str
    position: str
    current_level: str
    target_skills: List[str]
    recommended_drills: List[str]
    dryland_exercises: List[str]
    timeline_weeks: int
    progress_markers: List[str]

# Enhanced search function that searches across all content types
@mcp.tool("search_hockey_knowledge")
def search_hockey_knowledge(
    query: str, 
    content_types: Optional[List[str]] = None,
    complexity_levels: Optional[List[str]] = None,
    age_groups: Optional[List[str]] = None,
    n_results: int = 10
) -> List[HockeyKnowledgeResult]:
    """
    Universal search across all hockey knowledge types with intelligent filtering.
    
    Args:
        query: Search query
        content_types: Filter by types (drill, video, skill, tactic, rule, dryland)
        complexity_levels: Filter by complexity (beginner, intermediate, advanced)
        age_groups: Filter by age recommendations
        n_results: Number of results to return
    """
    logger.info(f"Universal search: query='{query}', types={content_types}, complexity={complexity_levels}")
    
    # Build dynamic where clause
    where_conditions = {}
    if content_types:
        # Map content types to actual prefixes in your data
        prefix_mapping = {
            'drill': 'drill-',
            'video': 'video-',
            'skill': 'ltad-',
            'tactic': 'tactic_',
            'rule': 'conduct-',
            'dryland': 'office-'
        }
        
    # Search with expanded results to allow for filtering
    results = collection.query(
        query_texts=[query],
        n_results=n_results * 3,  # Get more to filter from
        where=where_conditions if where_conditions else None
    )
    
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    
    unified_results: List[HockeyKnowledgeResult] = []
    
    for doc, meta, doc_id in zip(docs, metas, ids):
        # Determine content type from ID prefix
        content_type = _determine_content_type(doc_id)
        
        # Skip if content type filter doesn't match
        if content_types and content_type not in content_types:
            continue
            
        # Skip if complexity filter doesn't match
        if complexity_levels and meta.get('complexity', '').lower() not in [c.lower() for c in complexity_levels]:
            continue
            
        # Create unified result structure
        unified_result = _create_unified_result(doc, meta, doc_id, content_type)
        unified_results.append(unified_result)
        
        if len(unified_results) >= n_results:
            break
    
    logger.info(f"Returning {len(unified_results)} unified results")
    return unified_results

@mcp.tool("get_coaching_recommendations")
def get_coaching_recommendations(
    team_age: str,
    skill_focus: str,
    available_time: int,
    team_size: int,
    equipment_available: List[str]
) -> Dict[str, Any]:
    """
    Get personalized coaching recommendations based on team parameters.
    
    Args:
        team_age: Age group (e.g., "U8", "U12", "U16")
        skill_focus: Primary skill to work on (e.g., "skating", "shooting", "passing")
        available_time: Practice time in minutes
        team_size: Number of players
        equipment_available: List of available equipment
    """
    logger.info(f"Getting coaching recommendations for {team_age} team, focus: {skill_focus}")
    
    # Search for relevant content
    skill_results = search_hockey_knowledge(
        query=f"{skill_focus} {team_age}",
        content_types=["drill", "skill"],
        n_results=15
    )
    
    # Search for dryland exercises
    dryland_results = search_hockey_knowledge(
        query=f"{skill_focus} off ice training",
        content_types=["dryland"],
        n_results=5
    )
    
    # Use OpenAI to generate structured recommendations
    recommendation_prompt = f"""
    Based on the following hockey training content, create coaching recommendations for:
    - Team Age: {team_age}
    - Skill Focus: {skill_focus}
    - Practice Time: {available_time} minutes
    - Team Size: {team_size} players
    - Equipment: {equipment_available}
    
    Available drills and skills:
    {json.dumps([r for r in skill_results[:10]], indent=2)}
    
    Available dryland exercises:
    {json.dumps([r for r in dryland_results], indent=2)}
    
    Please provide:
    1. 3-5 recommended drills with time allocations
    2. Teaching points for coaches
    3. Common mistakes to watch for
    4. Progression suggestions
    5. Equipment setup tips
    
    Format as structured JSON.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert hockey coach. Provide practical, actionable coaching advice."},
                {"role": "user", "content": recommendation_prompt}
            ],
            temperature=0.7
        )
        
        recommendations = json.loads(response.choices[0].message.content)
        recommendations['source_content'] = {
            'drills_analyzed': len(skill_results),
            'dryland_options': len(dryland_results)
        }
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return {
            "error": "Could not generate recommendations",
            "available_drills": skill_results[:5],
            "available_dryland": dryland_results[:3]
        }

@mcp.tool("create_practice_plan")
def create_practice_plan(
    age_group: str,
    duration_minutes: int,
    focus_skills: List[str],
    number_of_players: int
) -> CoachingPlan:
    """
    Generate a complete practice plan with warm-up, main activities, and cool-down.
    """
    logger.info(f"Creating practice plan for {age_group}, {duration_minutes} min, skills: {focus_skills}")
    
    # Search for relevant content for each focus skill
    all_activities = []
    for skill in focus_skills:
        activities = search_hockey_knowledge(
            query=f"{skill} {age_group} drill",
            content_types=["drill", "skill"],
            n_results=5
        )
        all_activities.extend(activities)
    
    # Use AI to structure the practice plan
    plan_prompt = f"""
    Create a detailed {duration_minutes}-minute hockey practice plan for {age_group} with {number_of_players} players.
    Focus skills: {focus_skills}
    
    Available activities:
    {json.dumps(all_activities[:15], indent=2)}
    
    Structure the practice with:
    - Warm-up (10-15% of time)
    - Main activities (70-80% of time) 
    - Cool-down (10-15% of time)
    
    Include specific time allocations, setup instructions, and coaching points.
    Return as JSON matching the CoachingPlan structure.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional hockey coach creating detailed practice plans."},
                {"role": "user", "content": plan_prompt}
            ],
            temperature=0.6
        )
        
        plan_data = json.loads(response.choices[0].message.content)
        return CoachingPlan(**plan_data)
        
    except Exception as e:
        logger.error(f"Error creating practice plan: {e}")
        # Return a basic fallback plan
        return CoachingPlan(
            title=f"{age_group} Practice - {', '.join(focus_skills)}",
            age_group=age_group,
            duration_minutes=duration_minutes,
            focus_areas=focus_skills,
            warmup=[{"activity": "Basic skating", "duration": "10 min", "description": "Warm up with basic skating drills"}],
            main_activities=[{"activity": activity["title"], "duration": "15 min", "description": activity["summary"]} for activity in all_activities[:3]],
            cooldown=[{"activity": "Light skating", "duration": "5 min", "description": "Cool down with easy skating"}],
            equipment_needed=list(set([activity.get("equipment", "") for activity in all_activities if activity.get("equipment")])),
            coaching_notes="Adapt activities based on player skill level and engagement."
        )

@mcp.tool("analyze_player_development")
def analyze_player_development(
    player_position: str,
    current_skills: List[str],
    target_skills: List[str],
    timeline_weeks: int = 8
) -> PlayerDevelopmentPlan:
    """
    Create an individual player development plan with specific drills and progression.
    """
    logger.info(f"Creating development plan for {player_position}: {current_skills} -> {target_skills}")
    
    # Search for position-specific and skill-specific content
    development_content = []
    for skill in target_skills:
        content = search_hockey_knowledge(
            query=f"{skill} {player_position} development training",
            content_types=["drill", "skill", "dryland"],
            n_results=5
        )
        development_content.extend(content)
    
    # Generate development plan using AI
    dev_prompt = f"""
    Create a {timeline_weeks}-week individual development plan for a {player_position} player.
    Current skills: {current_skills}
    Target skills: {target_skills}
    
    Available training content:
    {json.dumps(development_content[:20], indent=2)}
    
    Include:
    - Progressive skill development over {timeline_weeks} weeks
    - Specific on-ice drills
    - Off-ice/dryland exercises
    - Measurable progress markers
    - Position-specific focuses
    
    Return as JSON matching PlayerDevelopmentPlan structure.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a hockey skills development coach creating personalized training plans."},
                {"role": "user", "content": dev_prompt}
            ],
            temperature=0.6
        )
        
        plan_data = json.loads(response.choices[0].message.content)
        return PlayerDevelopmentPlan(**plan_data)
        
    except Exception as e:
        logger.error(f"Error creating development plan: {e}")
        # Return basic fallback
        return PlayerDevelopmentPlan(
            player_name="Player",
            position=player_position,
            current_level="Developing",
            target_skills=target_skills,
            recommended_drills=[content["title"] for content in development_content[:5] if content.get("content_type") == "drill"],
            dryland_exercises=[content["title"] for content in development_content[:3] if content.get("content_type") == "dryland"],
            timeline_weeks=timeline_weeks,
            progress_markers=[f"Improve {skill} technique" for skill in target_skills]
        )

# Keep your existing specific tools but enhance them
@mcp.tool("find_drills_by_situation")
def find_drills_by_situation(
    game_situation: str,
    age_group: str = None,
    complexity: str = None,
    n_results: int = 5
) -> List[HockeyKnowledgeResult]:
    """
    Find drills for specific game situations (power play, penalty kill, breakout, etc.)
    """
    query = f"{game_situation} drill"
    if age_group:
        query += f" {age_group}"
    
    return search_hockey_knowledge(
        query=query,
        content_types=["drill", "tactic"],
        complexity_levels=[complexity] if complexity else None,
        n_results=n_results
    )

# Utility functions
def _determine_content_type(doc_id: str) -> str:
    """Determine content type from document ID prefix."""
    prefix = doc_id.split("-")[0] if "-" in doc_id else doc_id.split("_")[0]
    
    type_mapping = {
        "drill": "drill",
        "video": "video", 
        "ltad": "skill",
        "tactic": "tactic",
        "conduct": "rule",
        "office": "dryland",
        "insight": "interview",
        "dryland": "dryland"
    }
    
    return type_mapping.get(prefix, "unknown")

def _create_unified_result(doc: str, meta: Dict, doc_id: str, content_type: str) -> HockeyKnowledgeResult:
    """Create a unified result structure from any content type."""
    
    # Extract common fields with fallbacks
    base_result = {
        "id": doc_id,
        "title": meta.get("title", meta.get("skill_name", meta.get("tactic_name", "Untitled"))),
        "content_type": content_type,
        "summary": meta.get("summary", _parse_field(doc, "description") or doc[:200] + "..."),
        "complexity": meta.get("complexity", "intermediate"),
        "source": meta.get("source", "Unknown"),
        "age_recommendation": meta.get("age_group", meta.get("age_recommendation")),
        "equipment": meta.get("equipment", meta.get("equipment_needed")),
        "teaching_points": meta.get("teaching_points", _parse_field(doc, "teaching_points")),
        "skills_practiced": meta.get("skills", meta.get("hockey_skills", meta.get("skill_category"))),
        "positions": meta.get("positions", "All"),
        "url": meta.get("url", meta.get("video_url", meta.get("source_url"))),
        "metadata": meta
    }
    
    return base_result

def _parse_field(doc: str, label: str) -> str:
    """Extract a value for ``label`` from an indexed document."""
    prefix = label.lower() + ":"
    for line in doc.splitlines():
        if line.lower().startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""

# Resources for better integration
@mcp.resource("schema://unified_hockey_result")
def get_unified_schema() -> str:
    """Schema for unified hockey knowledge results."""
    return json.dumps({
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "title": {"type": "string"},
            "content_type": {"type": "string", "enum": ["drill", "video", "skill", "tactic", "rule", "dryland"]},
            "summary": {"type": "string"},
            "complexity": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]},
            "source": {"type": "string"},
            "age_recommendation": {"type": "string"},
            "equipment": {"type": "string"},
            "teaching_points": {"type": "string"},
            "skills_practiced": {"type": "string"},
            "positions": {"type": "string"},
            "url": {"type": "string"},
            "metadata": {"type": "object"}
        }
    })

@mcp.resource("coaching_tips://daily")
def get_daily_coaching_tip() -> str:
    """Provide a daily coaching tip based on current content."""
    # This could rotate through different tips or be based on seasonal focus
    tips = [
        "Focus on one skill at a time - players learn better with clear, specific objectives.",
        "Use positive reinforcement - catch players doing things right, not just wrong.",
        "Keep drills moving - idle time leads to lost attention and bad habits.",
        "Demonstrate skills yourself when possible - players learn visually.",
        "End practice on a positive note - leave players excited for next time."
    ]
    
    import random
    return random.choice(tips)

# Enhanced error handling and logging
def _safe_search(query: str, **kwargs) -> List[Dict]:
    """Wrapper for safe searching with error handling."""
    try:
        return collection.query(query_texts=[query], **kwargs)
    except Exception as e:
        logger.error(f"Search error for query '{query}': {e}")
        return {"documents": [[]], "metadatas": [[]], "ids": [[]]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.sse_app, host="0.0.0.0", port=8000)