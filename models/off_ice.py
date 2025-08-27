from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel
import warnings

# DEPRECATED: This model is legacy. Use EnrichedOffIceEntry from enriched_off_ice.py instead.
# This file is maintained for backward compatibility only.

class OffIceEntry(BaseModel):
    title: str
    category: str
    description: str
    source_page: int
    source: str = "off_ice_manual_hockey_canada_level1"

    age_recommendation: Optional[str] = None
    goals: Optional[List[str]] = None

    def is_valid(self) -> bool:
        return all([self.title.strip(), self.category.strip(), self.description.strip()])
