from __future__ import annotations

"""Enhanced MCP server for comprehensive hockey coaching knowledge base."""

from typing import List, Optional, Dict, Any, Union
from typing_extensions import TypedDict
from pydantic import BaseModel
import json
import logging
from openai import OpenAI
from datetime import datetime
import asyncio
import urllib.parse
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from mcp.server.fastmcp import FastMCP

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.chroma_utils import get_chroma_collection, get_client

mcp = FastMCP("Enhanced Hockey MCP Server", stateless_http=True)
# Note: Individual collections are accessed in each search tool
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

# ====== SPECIALIZED SEARCH TOOLS ======

@mcp.tool("search_hockey_tactics")
def search_hockey_tactics(
    query: str,
    tactic_types: Optional[List[str]] = None,
    positions: Optional[List[str]] = None,
    n_results: int = 10
) -> List[HockeyKnowledgeResult]:
    """
    Search for hockey tactics, systems, and strategic plays using a dedicated tactics collection.
    
    Args:
        query: Search query for tactics (e.g., "forechecking", "power play", "neutral zone")
        tactic_types: Optional filter for specific tactic types (e.g., ["power-play", "forechecking", "breakout"])
        positions: Optional filter for position-specific tactics (e.g., ["center", "defense", "winger"])
        n_results: Number of results to return
    """
    start_time = datetime.now()
    logger.info(f"🎯 [TOOL CALL] search_hockey_tactics: query='{query}', types={tactic_types}, positions={positions}, n_results={n_results}")
    
    try:
        # Get the dedicated tactics collection
        chroma_client = get_client()
        tactics_collection = chroma_client.get_collection(name="hockey_tactics")
        
        # Build where clause for filtering
        where_conditions = {}
        if tactic_types:
            # Map tactic types to skills in metadata
            skill_filters = []
            for tactic_type in tactic_types:
                skill_filters.append({"$contains": tactic_type})
            if len(skill_filters) == 1:
                where_conditions["skills"] = skill_filters[0]
            else:
                where_conditions["$or"] = [{"skills": sf} for sf in skill_filters]
        
        # Search the tactics collection
        logger.debug(f"Searching tactics collection with query: '{query}'")
        results = tactics_collection.query(
            query_texts=[query],
            n_results=n_results * 2,  # Get more to allow for filtering
            where=where_conditions if where_conditions else None
        )
        
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0] 
        ids = results.get("ids", [[]])[0]
        
        unified_results: List[HockeyKnowledgeResult] = []
        
        for doc, meta, doc_id in zip(docs, metas, ids):
            # Apply position filter if specified
            if positions:
                # Check if any of the specified positions are mentioned in assignments
                position_match = False
                for position in positions:
                    pos_lower = position.lower()
                    if (pos_lower in meta.get('centre_assignments', '').lower() or
                        pos_lower in meta.get('winger_assignments', '').lower() or 
                        pos_lower in meta.get('defense_assignments', '').lower() or
                        (pos_lower == 'goalie' and meta.get('goalie_assignments', '') != 'N/A')):
                        position_match = True
                        break
                
                if not position_match:
                    continue
            
            # Create unified result structure for tactics
            unified_result = _create_tactics_result(doc, meta, doc_id)
            unified_results.append(unified_result)
            
            if len(unified_results) >= n_results:
                break
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [TOOL COMPLETE] search_hockey_tactics: returned {len(unified_results)} tactics in {duration:.2f}s")
        return unified_results
        
    except Exception as e:
        logger.error(f"❌ Error searching hockey tactics: {e}")
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"❌ [TOOL ERROR] search_hockey_tactics failed in {duration:.2f}s")
        return []

@mcp.tool("search_hockey_videos")
def search_hockey_videos(
    query: str,
    n_results: int = 10
) -> List[HockeyKnowledgeResult]:
    """
    Search for hockey instructional videos and video clips.
    
    Args:
        query: Search query for videos (e.g., "skating technique", "shooting form", "drill demonstration")
        n_results: Number of results to return
    """
    start_time = datetime.now()
    logger.info(f"🎥 [TOOL CALL] search_hockey_videos: query='{query}', n_results={n_results}")
    
    try:
        # Get the dedicated hockey videos collection
        chroma_client = get_client()
        videos_collection = chroma_client.get_collection(name="hockey_videos")
        
        # Search the videos collection
        logger.debug(f"Searching videos collection with query: '{query}'")
        results = videos_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0] 
        ids = results.get("ids", [[]])[0]
        
        unified_results: List[HockeyKnowledgeResult] = []
        
        for doc, meta, doc_id in zip(docs, metas, ids):
            # Create unified result structure for videos
            unified_result = _create_videos_result(doc, meta, doc_id)
            unified_results.append(unified_result)
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [TOOL COMPLETE] search_hockey_videos: returned {len(unified_results)} videos in {duration:.2f}s")
        return unified_results
        
    except Exception as e:
        logger.error(f"❌ Error searching hockey videos: {e}")
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"❌ [TOOL ERROR] search_hockey_videos failed in {duration:.2f}s")
        return []

@mcp.tool("search_hockey_drills")
def search_hockey_drills(
    query: str,
    n_results: int = 10
) -> List[HockeyKnowledgeResult]:
    """
    Search for hockey drills and practice activities.
    
    Args:
        query: Search query for drills (e.g., "passing drill", "small area games", "power play practice")
        n_results: Number of results to return
    """
    start_time = datetime.now()
    logger.info(f"🏒 [TOOL CALL] search_hockey_drills: query='{query}', n_results={n_results}")
    
    try:
        # Get the dedicated hockey drills collection
        chroma_client = get_client()
        drills_collection = chroma_client.get_collection(name="hockey_drills")
        
        # Search the drills collection
        logger.debug(f"Searching drills collection with query: '{query}'")
        results = drills_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0] 
        ids = results.get("ids", [[]])[0]
        
        unified_results: List[HockeyKnowledgeResult] = []
        
        for doc, meta, doc_id in zip(docs, metas, ids):
            # Create unified result structure for drills
            unified_result = _create_drills_result(doc, meta, doc_id)
            unified_results.append(unified_result)
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [TOOL COMPLETE] search_hockey_drills: returned {len(unified_results)} drills in {duration:.2f}s")
        return unified_results
        
    except Exception as e:
        logger.error(f"❌ Error searching hockey drills: {e}")
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"❌ [TOOL ERROR] search_hockey_drills failed in {duration:.2f}s")
        return []

@mcp.tool("search_hockey_skills")
def search_hockey_skills(
    query: str,
    age_groups: Optional[List[str]] = None,
    n_results: int = 10
) -> List[HockeyKnowledgeResult]:
    """
    Search for hockey skill development and LTAD framework content.
    
    Args:
        query: Search query for skills (e.g., "U10 skating", "puck handling progression", "goalie development")
        age_groups: Optional filter for specific age groups (e.g., ["U10", "U12", "All Ages - Goalies"])
        n_results: Number of results to return
    """
    start_time = datetime.now()
    logger.info(f"⚡ [TOOL CALL] search_hockey_skills: query='{query}', age_groups={age_groups}, n_results={n_results}")
    
    try:
        # Get the dedicated hockey skills collection
        chroma_client = get_client()
        skills_collection = chroma_client.get_collection(name="hockey_skills")
        
        # Build where clause for filtering
        where_conditions = None
        if age_groups:
            # Create OR conditions for each age group
            # Using $eq for exact matching since ChromaDB doesn't support $contains
            if len(age_groups) == 1:
                where_conditions = {"age_group": {"$eq": age_groups[0]}}
            else:
                where_conditions = {"$or": [
                    {"age_group": {"$eq": age_group}} 
                    for age_group in age_groups
                ]}
            logger.debug(f"Applying age group filter: {age_groups}")
        
        # Search the skills collection
        logger.debug(f"Searching skills collection with query: '{query}', filters: {where_conditions}")
        results = skills_collection.query(
            query_texts=[query],
            n_results=n_results if not age_groups else n_results * 2,  # Get more results if filtering
            where=where_conditions
        )
        
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0] 
        ids = results.get("ids", [[]])[0]
        
        unified_results: List[HockeyKnowledgeResult] = []
        
        for doc, meta, doc_id in zip(docs, metas, ids):
            # Create unified result structure for skills
            unified_result = _create_skills_result(doc, meta, doc_id)
            unified_results.append(unified_result)
            
            # Stop if we've reached the requested number of results
            if len(unified_results) >= n_results:
                break
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [TOOL COMPLETE] search_hockey_skills: returned {len(unified_results)} skills in {duration:.2f}s")
        return unified_results
        
    except Exception as e:
        logger.error(f"❌ Error searching hockey skills: {e}")
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"❌ [TOOL ERROR] search_hockey_skills failed in {duration:.2f}s")
        return []

@mcp.tool("search_hockey_dryland")
def search_hockey_dryland(
    query: str,
    n_results: int = 10
) -> List[HockeyKnowledgeResult]:
    """
    Search for off-ice training and dryland exercises.
    
    Args:
        query: Search query for dryland (e.g., "balance training", "core strength", "agility exercises")
        n_results: Number of results to return
    """
    start_time = datetime.now()
    logger.info(f"🏋️ [TOOL CALL] search_hockey_dryland: query='{query}', n_results={n_results}")
    
    try:
        # Get the dedicated hockey dryland collection
        chroma_client = get_client()
        dryland_collection = chroma_client.get_collection(name="hockey_dryland")
        
        # Search the dryland collection
        logger.debug(f"Searching dryland collection with query: '{query}'")
        results = dryland_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0] 
        ids = results.get("ids", [[]])[0]
        
        unified_results: List[HockeyKnowledgeResult] = []
        
        for doc, meta, doc_id in zip(docs, metas, ids):
            # Create unified result structure for dryland
            unified_result = _create_dryland_result(doc, meta, doc_id)
            unified_results.append(unified_result)
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [TOOL COMPLETE] search_hockey_dryland: returned {len(unified_results)} dryland exercises in {duration:.2f}s")
        return unified_results
        
    except Exception as e:
        logger.error(f"❌ Error searching hockey dryland: {e}")
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"❌ [TOOL ERROR] search_hockey_dryland failed in {duration:.2f}s")
        return []

@mcp.tool("search_hockey_dryland_videos")
def search_hockey_dryland_videos(
    query: str,
    n_results: int = 10
) -> List[HockeyKnowledgeResult]:
    """
    Search for off-ice training video demonstrations and dryland video clips.
    
    Args:
        query: Search query for dryland videos (e.g., "plyometric exercises", "stick handling off ice", "training demonstrations")
        n_results: Number of results to return
    """
    start_time = datetime.now()
    logger.info(f"🎥🏋️ [TOOL CALL] search_hockey_dryland_videos: query='{query}', n_results={n_results}")
    
    try:
        # Get the dedicated hockey dryland videos collection
        chroma_client = get_client()
        dryland_videos_collection = chroma_client.get_collection(name="hockey_dryland_videos")
        
        # Search the dryland videos collection
        logger.debug(f"Searching dryland videos collection with query: '{query}'")
        results = dryland_videos_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0] 
        ids = results.get("ids", [[]])[0]
        
        unified_results: List[HockeyKnowledgeResult] = []
        
        for doc, meta, doc_id in zip(docs, metas, ids):
            # Create unified result structure for dryland videos
            unified_result = _create_dryland_videos_result(doc, meta, doc_id)
            unified_results.append(unified_result)
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [TOOL COMPLETE] search_hockey_dryland_videos: returned {len(unified_results)} dryland videos in {duration:.2f}s")
        return unified_results
        
    except Exception as e:
        logger.error(f"❌ Error searching hockey dryland videos: {e}")
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"❌ [TOOL ERROR] search_hockey_dryland_videos failed in {duration:.2f}s")
        return []

@mcp.tool("search_hockey_nhl_insights")
def search_hockey_nhl_insights(
    query: str,
    n_results: int = 10
) -> List[HockeyKnowledgeResult]:
    """
    Search for NHL coaching insights and professional hockey wisdom.
    
    Args:
        query: Search query for insights (e.g., "leadership advice", "coaching philosophy", "player development")
        n_results: Number of results to return
    """
    start_time = datetime.now()
    logger.info(f"🌟 [TOOL CALL] search_hockey_nhl_insights: query='{query}', n_results={n_results}")
    
    try:
        # Get the dedicated hockey NHL insights collection
        chroma_client = get_client()
        insights_collection = chroma_client.get_collection(name="hockey_nhl_insights")
        
        # Search the insights collection
        logger.debug(f"Searching NHL insights collection with query: '{query}'")
        results = insights_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0] 
        ids = results.get("ids", [[]])[0]
        
        unified_results: List[HockeyKnowledgeResult] = []
        
        for doc, meta, doc_id in zip(docs, metas, ids):
            # Create unified result structure for NHL insights
            unified_result = _create_nhl_insights_result(doc, meta, doc_id)
            unified_results.append(unified_result)
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [TOOL COMPLETE] search_hockey_nhl_insights: returned {len(unified_results)} insights in {duration:.2f}s")
        return unified_results
        
    except Exception as e:
        logger.error(f"❌ Error searching hockey NHL insights: {e}")
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"❌ [TOOL ERROR] search_hockey_nhl_insights failed in {duration:.2f}s")
        return []

# Removed tools - converted to resources below

@mcp.tool("search_hockey_rules")
def search_hockey_rules(
    query: str,
    n_results: int = 10
) -> List[HockeyKnowledgeResult]:
    """
    Search for hockey rules, regulations, and conduct guidelines.
    
    Args:
        query: Search query for rules (e.g., "body checking age", "icing rules", "penalty guidelines")
        n_results: Number of results to return
    """
    start_time = datetime.now()
    logger.info(f"⚖️ [TOOL CALL] search_hockey_rules: query='{query}', n_results={n_results}")
    
    try:
        # Get the dedicated hockey rules collection
        chroma_client = get_client()
        rules_collection = chroma_client.get_collection(name="hockey_rules")
        
        # Search the rules collection
        logger.debug(f"Searching rules collection with query: '{query}'")
        results = rules_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0] 
        ids = results.get("ids", [[]])[0]
        
        unified_results: List[HockeyKnowledgeResult] = []
        
        for doc, meta, doc_id in zip(docs, metas, ids):
            # Create unified result structure for rules
            unified_result = _create_rules_result(doc, meta, doc_id)
            unified_results.append(unified_result)
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ [TOOL COMPLETE] search_hockey_rules: returned {len(unified_results)} rules in {duration:.2f}s")
        return unified_results
        
    except Exception as e:
        logger.error(f"❌ Error searching hockey rules: {e}")
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"❌ [TOOL ERROR] search_hockey_rules failed in {duration:.2f}s")
        return []

# ====== REMOVED OLD GENERAL SEARCH TOOLS ======
# The following tools have been replaced with specialized search tools:
# - search_hockey_knowledge (replaced with specialized collection searches)
# - find_skills_by_age_group (replaced with search_hockey_skills)
# - find_rules_by_league_age (replaced with search_hockey_rules)
# - get_coaching_recommendations (removed - use specialized searches directly)
# - create_practice_plan (removed - use specialized searches directly)
# - analyze_player_development (removed - use specialized searches directly)

# ====== Utility Functions ======

def _process_search_results(search_results: dict, collection_name: str) -> List[HockeyKnowledgeResult]:
    """Process ChromaDB search results into unified HockeyKnowledgeResult format."""
    logger.debug(f"🔄 Processing search results from collection: {collection_name}")
    
    docs = search_results.get("documents", [[]])[0]
    metas = search_results.get("metadatas", [[]])[0]
    ids = search_results.get("ids", [[]])[0]
    
    logger.debug(f"Raw results: {len(docs)} docs, {len(metas)} metadata, {len(ids)} IDs")
    
    results = []
    for doc, meta, doc_id in zip(docs, metas, ids):
        try:
            content_type = _determine_content_type(doc_id)
            unified_result = _create_unified_result(doc, meta, doc_id, content_type)
            results.append(unified_result)
            logger.debug(f"Processed: {unified_result['title']} ({content_type})")
        except Exception as e:
            logger.warning(f"⚠️ Error processing result {doc_id}: {e}")
            continue
    
    logger.debug(f"Successfully processed {len(results)}/{len(docs)} results from {collection_name}")
    return results

def _determine_content_type(doc_id: str) -> str:
    """Determine content type from document ID prefix."""
    logger.debug(f"Determining content type for doc_id: {doc_id}")
    
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
    
    content_type = type_mapping.get(prefix, "unknown")
    logger.debug(f"Doc '{doc_id}' -> prefix '{prefix}' -> type '{content_type}'")
    
    return content_type

def _create_unified_result(doc: str, meta: Dict, doc_id: str, content_type: str) -> HockeyKnowledgeResult:
    """Create a unified result structure from any content type."""
    logger.debug(f"Creating unified result for {content_type} document: {doc_id}")
    
    # Extract common fields with fallbacks
    title = meta.get("title", meta.get("skill_name", meta.get("tactic_name", "Untitled")))
    base_result = {
        "id": doc_id,
        "title": title,
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
    
    logger.debug(f"Unified result created: '{title}' ({content_type})")
    return base_result

def _create_tactics_result(doc: str, meta: Dict, doc_id: str) -> HockeyKnowledgeResult:
    """Create a unified result structure specifically for hockey tactics."""
    logger.debug(f"Creating tactics result for document: {doc_id}")
    
    # Extract tactics-specific fields
    title = meta.get("tactic_name", "Untitled Tactic")
    summary = meta.get("summary", doc[:200] + "...")
    
    # Build teaching points from multiple sources
    teaching_points_parts = []
    if meta.get("teaching_points"):
        teaching_points_parts.append(meta["teaching_points"])
    
    # Add position-specific assignments as teaching points
    position_assignments = []
    if meta.get("centre_assignments"):
        position_assignments.append(f"Center: {meta['centre_assignments']}")
    if meta.get("winger_assignments"):
        position_assignments.append(f"Wingers: {meta['winger_assignments']}")
    if meta.get("defense_assignments"):
        position_assignments.append(f"Defense: {meta['defense_assignments']}")
    if meta.get("goalie_assignments") and meta["goalie_assignments"] != "N/A":
        position_assignments.append(f"Goalie: {meta['goalie_assignments']}")
    
    if position_assignments:
        teaching_points_parts.extend(position_assignments)
    
    teaching_points = "; ".join(teaching_points_parts) if teaching_points_parts else ""
    
    # Determine positions covered
    positions = []
    if meta.get("centre_assignments"):
        positions.append("Center")
    if meta.get("winger_assignments"):
        positions.append("Wingers")
    if meta.get("defense_assignments"):
        positions.append("Defense")
    if meta.get("goalie_assignments") and meta["goalie_assignments"] != "N/A":
        positions.append("Goalie")
    
    positions_str = ", ".join(positions) if positions else "All Positions"
    
    tactics_result = {
        "id": doc_id,
        "title": title,
        "content_type": "tactic",
        "summary": summary,
        "complexity": meta.get("complexity", "intermediate"),
        "source": meta.get("source", "Hockey Tactics"),
        "age_recommendation": None,  # Tactics are generally applicable across age groups
        "equipment": None,  # Tactics don't typically specify equipment
        "teaching_points": teaching_points,
        "skills_practiced": meta.get("skills", ""),
        "positions": positions_str,
        "url": None,
        "metadata": meta
    }
    
    logger.debug(f"Tactics result created: '{title}' (positions: {positions_str})")
    return tactics_result

def _create_videos_result(doc: str, meta: Dict, doc_id: str) -> HockeyKnowledgeResult:
    """Create a unified result structure specifically for hockey videos."""
    logger.debug(f"Creating videos result for document: {doc_id}")
    
    title = meta.get("clip_title", meta.get("title", "Untitled Video"))
    summary = meta.get("summary", meta.get("clip_description", doc[:200] + "..."))
    
    videos_result = {
        "id": doc_id,
        "title": title,
        "content_type": "video",
        "summary": summary,
        "complexity": meta.get("complexity", "intermediate"),
        "source": meta.get("source", "Hockey Videos"),
        "age_recommendation": meta.get("age_group", meta.get("age_recommendation")),
        "equipment": meta.get("equipment_needed"),
        "teaching_points": meta.get("teaching_points", _parse_field(doc, "teaching_points")),
        "skills_practiced": meta.get("skills_demonstrated", meta.get("hockey_skills")),
        "positions": meta.get("positions", "All"),
        "url": meta.get("video_url", meta.get("clip_url")),
        "metadata": meta
    }
    
    logger.debug(f"Videos result created: '{title}'")
    return videos_result

def _create_drills_result(doc: str, meta: Dict, doc_id: str) -> HockeyKnowledgeResult:
    """Create a unified result structure specifically for hockey drills."""
    logger.debug(f"Creating drills result for document: {doc_id}")
    
    title = meta.get("drill_name", meta.get("title", "Untitled Drill"))
    summary = meta.get("summary", meta.get("drill_description", doc[:200] + "..."))
    
    drills_result = {
        "id": doc_id,
        "title": title,
        "content_type": "drill",
        "summary": summary,
        "complexity": meta.get("complexity", meta.get("skill_level", "intermediate")),
        "source": meta.get("source", "Hockey Drills"),
        "age_recommendation": meta.get("age_group", meta.get("recommended_age")),
        "equipment": meta.get("equipment_needed", meta.get("equipment")),
        "teaching_points": meta.get("teaching_points", meta.get("coaching_tips", _parse_field(doc, "teaching_points"))),
        "skills_practiced": meta.get("skills_practiced", meta.get("hockey_skills")),
        "positions": meta.get("positions", "All"),
        "url": meta.get("source_url"),
        "metadata": meta
    }
    
    logger.debug(f"Drills result created: '{title}'")
    return drills_result

def _create_skills_result(doc: str, meta: Dict, doc_id: str) -> HockeyKnowledgeResult:
    """Create a unified result structure specifically for hockey skills."""
    logger.debug(f"Creating skills result for document: {doc_id}")
    
    title = meta.get("skill_name", meta.get("title", "Untitled Skill"))
    summary = meta.get("summary", meta.get("skill_description", doc[:200] + "..."))
    
    skills_result = {
        "id": doc_id,
        "title": title,
        "content_type": "skill",
        "summary": summary,
        "complexity": meta.get("complexity", meta.get("skill_level", "intermediate")),
        "source": meta.get("source", "Hockey Skills Development"),
        "age_recommendation": meta.get("age_group", meta.get("ltad_stage")),
        "equipment": meta.get("equipment_needed"),
        "teaching_points": meta.get("teaching_points", meta.get("key_concepts", _parse_field(doc, "teaching_points"))),
        "skills_practiced": meta.get("skill_category", meta.get("hockey_skills")),
        "positions": meta.get("positions", "All"),
        "url": meta.get("source_url"),
        "metadata": meta
    }
    
    logger.debug(f"Skills result created: '{title}'")
    return skills_result

def _create_dryland_result(doc: str, meta: Dict, doc_id: str) -> HockeyKnowledgeResult:
    """Create a unified result structure specifically for hockey dryland exercises."""
    logger.debug(f"Creating dryland result for document: {doc_id}")
    
    title = meta.get("exercise_name", meta.get("title", "Untitled Exercise"))
    summary = meta.get("summary", meta.get("exercise_description", doc[:200] + "..."))
    
    dryland_result = {
        "id": doc_id,
        "title": title,
        "content_type": "dryland",
        "summary": summary,
        "complexity": meta.get("complexity", meta.get("difficulty_level", "intermediate")),
        "source": meta.get("source", "Dryland Training"),
        "age_recommendation": meta.get("age_group", meta.get("recommended_age")),
        "equipment": meta.get("equipment_needed", meta.get("equipment")),
        "teaching_points": meta.get("teaching_points", meta.get("coaching_cues", _parse_field(doc, "coaching_cues"))),
        "skills_practiced": meta.get("hockey_skills_targeted", meta.get("benefits")),
        "positions": meta.get("positions", "All"),
        "url": meta.get("source_url"),
        "metadata": meta
    }
    
    logger.debug(f"Dryland result created: '{title}'")
    return dryland_result

def _create_dryland_videos_result(doc: str, meta: Dict, doc_id: str) -> HockeyKnowledgeResult:
    """Create a unified result structure specifically for hockey dryland videos."""
    logger.debug(f"Creating dryland videos result for document: {doc_id}")
    
    title = meta.get("clip_title", meta.get("title", "Untitled Dryland Video"))
    summary = meta.get("summary", meta.get("clip_description", doc[:200] + "..."))
    
    dryland_videos_result = {
        "id": doc_id,
        "title": title,
        "content_type": "dryland_video",
        "summary": summary,
        "complexity": meta.get("complexity", "intermediate"),
        "source": meta.get("source", "Dryland Training Videos"),
        "age_recommendation": meta.get("age_group", meta.get("age_recommendation")),
        "equipment": meta.get("equipment_needed"),
        "teaching_points": meta.get("teaching_points", _parse_field(doc, "teaching_points")),
        "skills_practiced": meta.get("skills_demonstrated", meta.get("hockey_skills_targeted")),
        "positions": meta.get("positions", "All"),
        "url": meta.get("video_url", meta.get("clip_url")),
        "metadata": meta
    }
    
    logger.debug(f"Dryland videos result created: '{title}'")
    return dryland_videos_result

def _create_nhl_insights_result(doc: str, meta: Dict, doc_id: str) -> HockeyKnowledgeResult:
    """Create a unified result structure specifically for NHL insights."""
    logger.debug(f"Creating NHL insights result for document: {doc_id}")
    
    title = meta.get("insight_title", meta.get("title", "Untitled Insight"))
    summary = meta.get("summary", meta.get("insight_summary", doc[:200] + "..."))
    
    nhl_insights_result = {
        "id": doc_id,
        "title": title,
        "content_type": "nhl_insight",
        "summary": summary,
        "complexity": meta.get("complexity", "advanced"),
        "source": meta.get("source", meta.get("expert_name", "NHL Insights")),
        "age_recommendation": None,  # NHL insights are generally for coaches/advanced players
        "equipment": None,  # Insights don't typically specify equipment
        "teaching_points": meta.get("key_points", meta.get("coaching_wisdom", _parse_field(doc, "key_points"))),
        "skills_practiced": meta.get("topics_covered", meta.get("expertise_area")),
        "positions": meta.get("position_focus", "All"),
        "url": meta.get("source_url"),
        "metadata": meta
    }
    
    logger.debug(f"NHL insights result created: '{title}'")
    return nhl_insights_result

def _create_rules_result(doc: str, meta: Dict, doc_id: str) -> HockeyKnowledgeResult:
    """Create a unified result structure specifically for hockey rules."""
    logger.debug(f"Creating rules result for document: {doc_id}")
    
    title = meta.get("rule_title", meta.get("title", "Untitled Rule"))
    summary = meta.get("summary", meta.get("rule_description", doc[:200] + "..."))
    
    rules_result = {
        "id": doc_id,
        "title": title,
        "content_type": "rule",
        "summary": summary,
        "complexity": meta.get("complexity", "intermediate"),
        "source": meta.get("source", "Hockey Rules & Regulations"),
        "age_recommendation": meta.get("age_group", meta.get("applicable_ages")),
        "equipment": None,  # Rules don't typically specify equipment
        "teaching_points": meta.get("key_points", meta.get("implementation_notes", _parse_field(doc, "key_points"))),
        "skills_practiced": None,  # Rules don't practice skills directly
        "positions": meta.get("position_specific", "All"),
        "url": meta.get("source_url"),
        "metadata": meta
    }
    
    logger.debug(f"Rules result created: '{title}'")
    return rules_result

def _parse_field(doc: str, label: str) -> str:
    """Extract a value for ``label`` from an indexed document."""
    logger.debug(f"Parsing field '{label}' from document")
    
    prefix = label.lower() + ":"
    for line in doc.splitlines():
        if line.lower().startswith(prefix):
            value = line.split(":", 1)[1].strip()
            logger.debug(f"Found {label}: {value[:50]}{'...' if len(value) > 50 else ''}")
            return value
    
    logger.debug(f"Field '{label}' not found in document")
    return ""

# Removed old utility functions that were only used by the removed general tools:
# - _validate_time_allocations (was used by create_practice_plan)
# - _extract_minutes (was used by _validate_time_allocations) 
# - _create_flexible_fallback_plan (was used by create_practice_plan)

# ====== RESOURCES ======
# Resources for better integration

@mcp.resource("hockey://skills/by-age/{age_group}")
def get_skills_by_age_group(uri: str) -> str:
    """Get all skills for a specific age group.
    
    Returns a list of all skill titles and categories for the specified age group,
    without pagination limits. This is useful for getting a complete overview of
    available skills.
    
    URI Examples:
    - hockey://skills/by-age/U11
    - hockey://skills/by-age/U13
    - hockey://skills/by-age/All%20Ages%20-%20Goalies
    
    Args:
        uri: Resource URI in format hockey://skills/by-age/{age_group}
    
    Returns:
        JSON string containing all skills for the age group
    """
    # Parse age group from URI
    import re
    import urllib.parse
    
    match = re.match(r"hockey://skills/by-age/(.+)", uri)
    if not match:
        return json.dumps({"error": "Invalid URI format"})
    
    # Decode URL-encoded age groups
    age_group = urllib.parse.unquote(match.group(1))
    
    try:
        logger.info(f"📋 [RESOURCE] Fetching skills for age group: {age_group}")
        
        # Get skills collection
        client = get_client()
        collection = client.get_collection(name="hockey_skills")
        
        # Use get() to retrieve all matching documents
        results = collection.get(
            where={"age_group": {"$eq": age_group}},
            limit=1000,  # Get up to 1000 skills
            include=["metadatas"]
        )
        
        if not results['metadatas']:
            return json.dumps({
                "age_group": age_group,
                "skills": [],
                "count": 0
            })
        
        # Extract skill information
        skills = []
        for metadata in results['metadatas']:
            if metadata:
                skills.append({
                    "skill_name": metadata.get("skill_name", "Unknown"),
                    "skill_category": metadata.get("skill_category", "Unknown"),
                    "complexity": metadata.get("complexity", ""),
                    "positions": metadata.get("positions", "").split("; ") if metadata.get("positions") else []
                })
        
        # Sort by category and name for better organization
        skills.sort(key=lambda x: (x["skill_category"], x["skill_name"]))
        
        logger.info(f"✅ [RESOURCE] Found {len(skills)} skills for {age_group}")
        
        return json.dumps({
            "age_group": age_group,
            "skills": skills,
            "count": len(skills)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"❌ Error fetching skills for age group {age_group}: {e}")
        return json.dumps({"error": str(e)})


@mcp.resource("hockey://skills/age-groups")
def get_available_age_groups() -> str:
    """Get all available age groups in the skills database.
    
    Returns a list of all age groups with skill counts for each.
    
    Returns:
        JSON string containing age groups and their skill counts
    """
    try:
        logger.info("📋 [RESOURCE] Fetching available age groups")
        
        # Get skills collection
        client = get_client()
        collection = client.get_collection(name="hockey_skills")
        
        # Get all documents to extract age groups
        results = collection.get(
            limit=1000,  # Get up to 1000 skills
            include=["metadatas"]
        )
        
        if not results['metadatas']:
            return json.dumps({
                "age_groups": [],
                "total_skills": 0
            })
        
        # Count skills by age group
        from collections import Counter
        age_group_counts = Counter()
        
        for metadata in results['metadatas']:
            if metadata and metadata.get("age_group"):
                age_group_counts[metadata["age_group"]] += 1
        
        # Format results
        age_groups = [
            {
                "age_group": age_group,
                "skill_count": count
            }
            for age_group, count in sorted(age_group_counts.items())
        ]
        
        logger.info(f"✅ [RESOURCE] Found {len(age_groups)} unique age groups")
        
        return json.dumps({
            "age_groups": age_groups,
            "total_skills": sum(age_group_counts.values())
        }, indent=2)
        
    except Exception as e:
        logger.error(f"❌ Error fetching available age groups: {e}")
        return json.dumps({"error": str(e)})

@mcp.resource("hockey://schema/unified_result")
def get_unified_schema() -> str:
    """Schema for unified hockey knowledge results."""
    return json.dumps({
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "title": {"type": "string"},
            "content_type": {"type": "string", "enum": ["drill", "video", "skill", "tactic", "rule", "dryland", "dryland_video", "nhl_insight"]},
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

if __name__ == "__main__":
    import os
    
    logger.info("🚀 Starting Hockey MCP Server...")
    
    # Test ChromaDB connection
    try:
        from utils.chroma_utils import get_client
        chroma_client = get_client()
        collections = chroma_client.list_collections()
        logger.info(f"✅ ChromaDB connected - {len(collections)} collections available")
        for coll in collections:
            count = coll.count()
            logger.debug(f"  - {coll.name}: {count} documents")
    except Exception as e:
        logger.error(f"❌ ChromaDB connection failed: {e}")
    
    # Test OpenAI connection
    try:
        import openai
        test_client = openai.OpenAI()
        logger.info("✅ OpenAI client initialized")
    except Exception as e:
        logger.error(f"❌ OpenAI initialization failed: {e}")
    
    logger.info("🏒 Hockey MCP Server ready for coaching!")
    logger.info("🔧 FastMCP Configuration: stateless_http=True")
    logger.info("🎯 This should prevent OpenAI session termination issues")
    
    # Support multiple transports for OpenAI compatibility
    transport = os.getenv('MCP_TRANSPORT', 'dual')
    port = int(os.getenv('MCP_PORT', '8000'))
    host = os.getenv('MCP_HOST', '0.0.0.0')
    
    logger.info(f"🚀 Transport mode: {transport}")
    
    if transport == 'stdio':
        logger.info("   → Starting STDIO transport (development)")
        mcp.run(transport="stdio")
    elif transport == 'sse':
        logger.info(f"   → Starting SSE server: http://{host}:{port}")
        import uvicorn
        uvicorn.run(mcp.sse_app, host=host, port=port)
    elif transport == 'streamable-http':
        logger.info(f"   → Starting Streamable-HTTP transport: http://{host}:{port}")
        import uvicorn
        uvicorn.run(mcp.streamable_http_app, host=host, port=port)
    else:  # Use streamable-http (preferred by OpenAI)
        logger.info(f"   → Starting Streamable-HTTP transport: http://{host}:{port}")
        logger.info("   → This is the preferred transport for OpenAI Responses API")
        logger.info("   → Session termination issue may be related to OpenAI timeout, not transport")
        
        # Research shows streamable-http is actively developed and preferred
        # SSE is deprecated in FastMCP
        import uvicorn
        uvicorn.run(mcp.streamable_http_app, host=host, port=port)