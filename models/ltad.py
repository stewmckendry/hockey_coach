from __future__ import annotations
from typing import List
from pydantic import BaseModel

class LTADSkill(BaseModel):
    age_group: str | None = None
    ltad_stage: str | None = None
    position: List[str] | None = None
    skill_category: str | None = None
    skill_name: str | None = None
    teaching_notes: str | None = None
    season_month: str | None = None
    source: str
