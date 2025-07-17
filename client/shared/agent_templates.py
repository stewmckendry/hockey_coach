from __future__ import annotations

from typing import Type, TypeVar, List

from pydantic import BaseModel
from agents import Agent

# Generic type variable for context models
C = TypeVar("C", bound=BaseModel)

def create_intake_agent(
    context_class: Type[C],
    prompt: str,
    tools: List,
    name: str,
) -> Agent[C]:
    """Return a typed intake Agent configured with the given prompt and tools."""
    return Agent[context_class](
        name=name,
        instructions=prompt,
        tools=tools,
        model="gpt-4o",
    )
