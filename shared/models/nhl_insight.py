from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class NHLInsight(BaseModel):
    """Structured insight extracted from an NHL article."""

    id: str
    speaker: Optional[str] = None
    quote: str
    question: Optional[str] = None
    context: Optional[str] = None
    tags: List[str]
    takeaways_for_coach: Optional[str] = None
    takeaways_for_player: Optional[str] = None
    source_url: HttpUrl
    source_article: str
    source_type: str = "MLHS"
    published_date: date
    author: Optional[str] = None
