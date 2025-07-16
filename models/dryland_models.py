from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class DrylandPlanOutput(BaseModel):
    start_date: date
    weeks: int
    weekly_focus: dict[str, str]
    template_session: dict[str, str]
    goals: List[str]


class DrylandSessionOutput(BaseModel):
    date: date
    focus_area: str
    warmup: List[str]
    main_set: List[str]
    cooldown: List[str]
    equipment_needed: List[str]
    video_refs: List[str]


class DrylandContext(BaseModel):
    age_group: Optional[str] = None
    season_phase: Optional[str] = None  # pre/in/post
    team_level: Optional[str] = None
    equipment: List[str] = []
    space: Optional[str] = None
    plan: Optional[DrylandPlanOutput] = None
    notes: Optional[str] = None

