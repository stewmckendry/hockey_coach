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

# ====== SEARCH TOOLS ======

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

# ===== PRACTICE PLAN TOOLS =====

@mcp.tool("create_practice_plan")
def create_practice_plan(
    age_group: str,
    duration_minutes: int,
    skill_focus_areas: List[Dict[str, Union[str, int]]],  # [{"skill": "skating", "time_minutes": 20}, {"skill": "shooting", "time_minutes": 15}]
    number_of_players: int,
    practice_context: str = "",  # Free text: "first practice back", "preparing for tournament", "working on power play", etc.
    team_systems_focus: Optional[List[str]] = None,  # ["breakouts", "forechecking", "power play"]
    include_dryland: bool = False,
    equipment_available: Optional[List[str]] = None,
    coaching_priorities: Optional[str] = None  # Free text coaching notes
) -> CoachingPlan:
    """
    Create a flexible practice plan based on coach's specific time allocations and priorities.
    
    Args:
        age_group: Age group (e.g., "U8", "U12", "U16") 
        duration_minutes: Total practice time
        skill_focus_areas: List of skills with desired time allocation
            Example: [{"skill": "skating", "time_minutes": 20}, {"skill": "shooting", "time_minutes": 15}, {"skill": "puck_handling", "time_minutes": 10}]
        number_of_players: Team size
        practice_context: Open text describing practice purpose/context
        team_systems_focus: Optional systems to emphasize (breakouts, forechecking, etc.)
        include_dryland: Include off-ice component
        equipment_available: Available equipment constraints
        coaching_priorities: Additional coaching notes/priorities
    """
    logger.info(f"Creating flexible practice plan for {age_group}: {skill_focus_areas}")
    
    # Calculate time allocations
    total_skill_time = sum(area.get('time_minutes', 0) for area in skill_focus_areas)
    warmup_time = max(8, duration_minutes * 0.12)  # 12% minimum 8 min
    cooldown_time = max(5, duration_minutes * 0.08)  # 8% minimum 5 min
    available_main_time = duration_minutes - warmup_time - cooldown_time
    
    # Validate time allocation
    if total_skill_time > available_main_time:
        logger.warning(f"Requested skill time ({total_skill_time} min) exceeds available time ({available_main_time} min)")
        # Proportionally adjust if over time
        adjustment_factor = available_main_time / total_skill_time
        for area in skill_focus_areas:
            area['time_minutes'] = int(area['time_minutes'] * adjustment_factor)
    
    # Comprehensive knowledge gathering for all requested skills
    knowledge_sources = {
        'on_ice_drills': [],
        'development_skills': [], 
        'tactical_systems': [],
        'video_instructions': [],
        'dryland_exercises': [],
        'coaching_insights': [],
        'team_systems': []
    }
    
    # Search for each skill area
    all_skills = [area['skill'] for area in skill_focus_areas]
    for skill_area in skill_focus_areas:
        skill = skill_area['skill']
        time_requested = skill_area['time_minutes']
        
        logger.info(f"Gathering knowledge for {skill} ({time_requested} min)")
        
        # On-ice drill search - get more results for skills with more time
        drill_count = max(3, min(8, time_requested // 5))  # 3-8 drills based on time
        drill_results = collection.query(
            query_texts=[f"{skill} {age_group} drill practice"],
            n_results=drill_count * 2,  # Get extras to filter
            where={"document_type": {"$ne": "off_ice_workout"}}
        )
        
        # LTAD skills search
        skill_results = collection.query(
            query_texts=[f"{skill} {age_group} development technique"],
            n_results=4
        )
        
        # Video instruction search
        video_results = collection.query(
            query_texts=[f"{skill} instruction teaching technique"],
            n_results=3,
            where={"clip_type": {"$ne": "off_ice_video"}}
        )
        
        # Coaching insights
        insight_results = collection.query(
            query_texts=[f"{skill} coaching tips advice NHL"],
            n_results=2
        )
        
        # Add to knowledge sources with skill tagging
        knowledge_sources['on_ice_drills'].extend(_process_search_results(drill_results, skill, "drill"))
        knowledge_sources['development_skills'].extend(_process_search_results(skill_results, skill, "skill"))
        knowledge_sources['video_instructions'].extend(_process_search_results(video_results, skill, "video"))
        knowledge_sources['coaching_insights'].extend(_process_search_results(insight_results, skill, "insight"))
    
    # Search for team systems if specified
    if team_systems_focus:
        for system in team_systems_focus:
            system_results = collection.query(
                query_texts=[f"{system} hockey system tactic positioning"],
                n_results=4
            )
            knowledge_sources['team_systems'].extend(_process_search_results(system_results, system, "tactic"))
    
    # Search for dryland if requested
    if include_dryland:
        for skill_area in skill_focus_areas:
            skill = skill_area['skill']
            dryland_results = collection.query(
                query_texts=[f"{skill} off ice training dryland"],
                n_results=3,
                where={"document_type": "off_ice_workout"}
            )
            knowledge_sources['dryland_exercises'].extend(_process_search_results(dryland_results, skill, "dryland"))
    
    # Get context-specific insights if practice context provided
    context_insights = []
    if practice_context:
        context_results = collection.query(
            query_texts=[f"{practice_context} coaching advice preparation"],
            n_results=3
        )
        context_insights = _process_search_results(context_results, "context", "insight")
    
    # Build comprehensive prompt
    plan_prompt = f"""
    Create a detailed {duration_minutes}-minute hockey practice plan for {age_group} with {number_of_players} players.
    
    COACH'S SPECIFIC REQUIREMENTS:
    Practice Context: {practice_context}
    Skill Focus Areas with Time Allocation:
    {json.dumps(skill_focus_areas, indent=2)}
    
    Team Systems Focus: {team_systems_focus or "None specified"}
    Include Dryland: {include_dryland}
    Equipment Constraints: {equipment_available or "Standard equipment assumed"}
    Additional Coaching Priorities: {coaching_priorities or "None specified"}
    
    TIME STRUCTURE:
    - Warm-up: {warmup_time:.0f} minutes
    - Main Practice: {available_main_time:.0f} minutes (allocated per coach's skill focus)
    - Cool-down: {cooldown_time:.0f} minutes
    
    COMPREHENSIVE KNOWLEDGE BASE:
    
    ON-ICE DRILLS ({len(knowledge_sources['on_ice_drills'])} available):
    {json.dumps(knowledge_sources['on_ice_drills'][:10], indent=2)}
    
    LTAD DEVELOPMENT SKILLS ({len(knowledge_sources['development_skills'])} available):
    {json.dumps(knowledge_sources['development_skills'][:6], indent=2)}
    
    VIDEO INSTRUCTIONS ({len(knowledge_sources['video_instructions'])} available):
    {json.dumps(knowledge_sources['video_instructions'][:6], indent=2)}
    
    NHL COACHING INSIGHTS ({len(knowledge_sources['coaching_insights'])} available):
    {json.dumps(knowledge_sources['coaching_insights'][:4], indent=2)}
    
    {f"TEAM SYSTEMS ({len(knowledge_sources['team_systems'])} available): {json.dumps(knowledge_sources['team_systems'][:5], indent=2)}" if team_systems_focus else ""}
    
    {f"DRYLAND EXERCISES ({len(knowledge_sources['dryland_exercises'])} available): {json.dumps(knowledge_sources['dryland_exercises'][:4], indent=2)}" if include_dryland else ""}
    
    {f"CONTEXT INSIGHTS: {json.dumps(context_insights[:3], indent=2)}" if context_insights else ""}
    
    INTEGRATION REQUIREMENTS:
    1. RESPECT TIME ALLOCATIONS: Each skill area must get approximately the time the coach requested
    2. COMPREHENSIVE INTEGRATION: Use multiple knowledge sources (drills + skills + videos + insights)
    3. LOGICAL FLOW: Activities should build progressively and complement each other
    4. COACHING DEPTH: Rich teaching points, setup details, common mistakes, progressions
    5. CONTEXT AWARENESS: Address the specific practice context provided
    6. SYSTEMS INTEGRATION: Incorporate team systems focus if specified
    
    OUTPUT FORMAT (JSON):
    {{
        "title": "Descriptive title reflecting coach's focus and context",
        "age_group": "{age_group}",
        "duration_minutes": {duration_minutes},
        "practice_context": "{practice_context}",
        "focus_areas": {all_skills},
        "time_allocation": {dict((area['skill'], area['time_minutes']) for area in skill_focus_areas)},
        "warmup": [
            {{
                "activity": "name",
                "duration": "{warmup_time:.0f} min",
                "description": "detailed description",
                "source_type": "drill/skill/video",
                "setup": "ice setup and equipment",
                "teaching_points": "key coaching cues",
                "purpose": "prepare players for main practice focus"
            }}
        ],
        "main_activities": [
            {{
                "activity": "name", 
                "duration": "X min (match coach's requested time)",
                "skill_focus": "which requested skill this addresses",
                "description": "detailed activity description",
                "source_type": "drill/skill/tactic/video", 
                "source_details": "brief note on knowledge source used",
                "setup": "ice organization and equipment needs",
                "teaching_points": "coaching cues from multiple sources",
                "nhl_insights": "relevant professional coaching wisdom",
                "progressions": "make it easier/harder",
                "common_mistakes": "what to watch for",
                "coaching_emphasis": "key points for this skill/time allocation"
            }}
        ],
        "cooldown": [
            {{
                "activity": "name",
                "duration": "{cooldown_time:.0f} min", 
                "description": "activity description and purpose"
            }}
        ],
        {f'"dryland_component": [{{"exercises": "specific exercises", "duration": "X min", "skill_connection": "how it connects to on-ice skills"}}],' if include_dryland else ''}
        "equipment_needed": ["organized clean list"],
        "coaching_notes": "Practice-specific insights addressing coach's context and priorities",
        "skill_time_breakdown": "confirmation of time allocation per skill",
        "systems_integration": "how team systems were incorporated if applicable",
        "knowledge_sources_utilized": "summary of sources used from knowledge base"
    }}
    
    CRITICAL SUCCESS FACTORS:
    - Honor the coach's specific time requests for each skill
    - Address the practice context meaningfully 
    - Integrate insights from multiple knowledge sources
    - Provide actionable coaching guidance beyond basic drill descriptions
    - Ensure activities flow logically and build on each other
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert hockey coach with access to comprehensive hockey knowledge. Create practice plans that precisely match the coach's time allocations and integrate wisdom from multiple sources. Always respect the specific time requests and context provided."},
                {"role": "user", "content": plan_prompt}
            ],
            temperature=0.6
        )
        
        plan_data = json.loads(response.choices[0].message.content)
        
        # Validate time allocations match requests
        if 'main_activities' in plan_data:
            _validate_time_allocations(plan_data, skill_focus_areas)
        
        # Add metadata about knowledge utilization
        plan_data['knowledge_sources_used'] = {
            'total_sources': sum(len(v) for v in knowledge_sources.values()),
            'drills': len(knowledge_sources['on_ice_drills']),
            'ltad_skills': len(knowledge_sources['development_skills']),
            'videos': len(knowledge_sources['video_instructions']),
            'nhl_insights': len(knowledge_sources['coaching_insights']),
            'team_systems': len(knowledge_sources['team_systems']),
            'dryland': len(knowledge_sources['dryland_exercises']) if include_dryland else 0
        }
        
        return CoachingPlan(**plan_data)
        
    except Exception as e:
        logger.error(f"Error creating flexible practice plan: {e}")
        return _create_flexible_fallback_plan(
            age_group, duration_minutes, skill_focus_areas, 
            practice_context, knowledge_sources, include_dryland
        )

# ====== Player DEVELOPMENT TOOLS ======

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

# ====== Utility Functions ======

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

def _validate_time_allocations(plan_data: dict, requested_allocations: List[Dict]) -> None:
    """Validate that the generated plan respects time allocations."""
    for skill_request in requested_allocations:
        skill = skill_request['skill']
        requested_time = skill_request['time_minutes']
        
        # Find activities addressing this skill
        skill_activities = [a for a in plan_data.get('main_activities', []) 
                           if a.get('skill_focus', '').lower() == skill.lower()]
        
        if not skill_activities:
            logger.warning(f"No activities found for requested skill: {skill}")
        else:
            # Sum up time for this skill (rough validation)
            total_time = sum(_extract_minutes(a.get('duration', '0 min')) for a in skill_activities)
            if abs(total_time - requested_time) > 5:  # Allow 5 min variance
                logger.warning(f"Time allocation mismatch for {skill}: requested {requested_time} min, got ~{total_time} min")

def _extract_minutes(duration_str: str) -> int:
    """Extract minutes from duration string like '15 min'."""
    try:
        return int(duration_str.split()[0])
    except:
        return 0

def _create_flexible_fallback_plan(
    age_group: str, 
    duration_minutes: int, 
    skill_focus_areas: List[Dict],
    practice_context: str,
    knowledge_sources: dict,
    include_dryland: bool
) -> CoachingPlan:
    """Create a fallback plan that still respects the coach's time allocations."""
    
    main_activities = []
    
    # Create activities for each requested skill with requested time
    for skill_area in skill_focus_areas:
        skill = skill_area['skill']
        time_requested = skill_area['time_minutes']
        
        # Find best available content for this skill
        skill_drills = [d for d in knowledge_sources['on_ice_drills'] 
                       if skill.lower() in d.get('addresses_skill', '').lower()]
        
        if skill_drills:
            drill = skill_drills[0]
            activity = {
                "activity": drill['title'],
                "duration": f"{time_requested} min",
                "skill_focus": skill,
                "description": drill['summary'],
                "source_type": "drill",
                "teaching_points": drill.get('teaching_points', ''),
                "setup": f"Equipment: {drill.get('equipment', 'Standard')}"
            }
        else:
            # Generic fallback maintaining time allocation
            activity = {
                "activity": f"{skill.title()} Development",
                "duration": f"{time_requested} min",
                "skill_focus": skill, 
                "description": f"Focused {skill} development for {age_group}",
                "source_type": "generic",
                "teaching_points": f"Emphasize proper {skill} technique and progression"
            }
        
        main_activities.append(activity)
    
    return CoachingPlan(
        title=f"{age_group} Custom Practice - {practice_context or 'Multi-Skill Focus'}",
        age_group=age_group,
        duration_minutes=duration_minutes,
        focus_areas=[area['skill'] for area in skill_focus_areas],
        warmup=[{
            "activity": "Dynamic warm-up",
            "duration": "10 min",
            "description": "Progressive skating warm-up tailored to practice focus"
        }],
        main_activities=main_activities,
        cooldown=[{
            "activity": "Cool-down and review",
            "duration": "5 min", 
            "description": "Light activity and practice summary"
        }],
        equipment_needed=["Pucks", "Cones", "Nets", "Boards"],
        coaching_notes=f"Fallback plan honoring coach's time allocations. Context: {practice_context}. Total knowledge sources: {sum(len(v) for v in knowledge_sources.values())}"
    )

# ====== RESOURCES ======
# Resources for better integration
@mcp.resource("hockey://schema/unified_result")
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

@mcp.resource("hockey://tips/daily")
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