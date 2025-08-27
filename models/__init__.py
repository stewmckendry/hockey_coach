"""
Models package for hockey coaching data structures.

This package contains Pydantic models for various hockey-related data:
- conduct: Policy and rulebook entries
- dryland_models: Dryland training and session planning
- ltad: Long Term Athlete Development skills
- nhl_insight: Professional hockey insights and quotes
- mlhs_article: Maple Leafs Hot Stove article data
- off_ice: Off-ice training activities (legacy - use enriched_off_ice)
- enriched_off_ice: Enhanced off-ice training with metadata
"""

__all__ = [
    "ConductEntry",
    "DrylandPlanOutput", 
    "DrylandSessionOutput",
    "DrylandContext",
    "LTADSkill",
    "NHLInsight", 
    "MLHSArticle",
    "OffIceEntry",
    "EnrichedOffIceEntry",
]