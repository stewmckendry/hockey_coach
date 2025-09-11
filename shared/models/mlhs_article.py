from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, HttpUrl


class MLHSArticle(BaseModel):
    """Raw article data from Maple Leafs Hot Stove."""

    title: str
    url: HttpUrl
    author: Optional[str]
    published_date: date
    category: Optional[str]
    excerpt: Optional[str]
    html_content: str
    page_number: int
