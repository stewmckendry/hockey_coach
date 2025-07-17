from __future__ import annotations

from typing import Union, List, Literal

from agents import function_tool, RunContextWrapper

from models.dryland_models import DrylandContext


@function_tool
async def set_dryland_context_param(
    ctx: RunContextWrapper[DrylandContext],
    key: Literal[
        "age_group",
        "season_phase",
        "team_level",
        "equipment",
        "space",
        "weeks",
        "notes"
    ],
    value: Union[str, List[str]],
) -> str:
    if isinstance(value, list):
        setattr(ctx.context, key, value)
    else:
        setattr(ctx.context, key, str(value))
    return f"{key} set"

