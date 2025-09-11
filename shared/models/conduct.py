from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class ConductEntry(BaseModel):
    """Structured policy or rulebook entry."""

    title: str
    content: str
    role: Optional[str] = None
    topic: Optional[str] = None
    document_type: Optional[str] = None
    source: str
    page: Optional[int] = None
