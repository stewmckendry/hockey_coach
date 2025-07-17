from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional

# ✅ Replaces `dict[str, str]` for weekly focus
class WeeklyFocusBlock(BaseModel):
    week: int
    focus: str

# ✅ Replaces `dict[str, str]` for session structure
class TemplateSessionBlock(BaseModel):
    warmup: str
    main: str
    cooldown: str

class DrylandPlanOutput(BaseModel):
    start_date: date
    weeks: int
    weekly_focus: List[WeeklyFocusBlock]  # ✅ List of models instead of dict
    template_session: TemplateSessionBlock
    goals: List[str] = Field(default_factory=list)

class DrylandSessionOutput(BaseModel):
    date: date
    focus_area: str
    warmup: List[str] = Field(default_factory=list)  # ✅ avoids 'default' in JSON Schema
    main_set: List[str] = Field(default_factory=list)
    cooldown: List[str] = Field(default_factory=list)
    equipment_needed: List[str] = Field(default_factory=list)
    video_refs: List[str] = Field(default_factory=list)

class DrylandContext(BaseModel):
    age_group: Optional[str] = None
    season_phase: Optional[str] = None  # pre/in/post
    team_level: Optional[str] = None
    equipment: List[str] = []
    space: Optional[str] = None
    weeks: Optional[int] = None  # ✅ New field added
    plan: Optional[DrylandPlanOutput] = None
    notes: Optional[str] = None

