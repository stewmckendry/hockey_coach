from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel

class EnrichedOffIceEntry(BaseModel):
    """Off-ice manual entry with additional metadata for indexing."""

    title: str
    category: str
    description: str
    source_pages: List[int]
    source: str = "off_ice_manual_hockey_canada_level1"

    age_recommendation: Optional[str] = None
    goals: Optional[List[str]] = None

    focus_area: str
    teaching_complexity: str
    progression_stage: str
    equipment_needed: Optional[str] = None
    safety_notes: Optional[str] = None
