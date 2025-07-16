from __future__ import annotations

from typing import Any

from agents import function_tool, RunContextWrapper

from models.dryland_models import DrylandContext


@function_tool
def set_dryland_context_param(
    ctx: RunContextWrapper[DrylandContext], key: str, value: Any
) -> str:
    """Update a value in the dryland session context."""
    if ctx.context is None:
        ctx.context = DrylandContext()
    if not hasattr(ctx.context, key):
        raise ValueError(f"Unknown context key: {key}")
    if key == "equipment":
        if isinstance(value, str):
            ctx.context.equipment = [v.strip() for v in value.split(',') if v.strip()]
        elif isinstance(value, list):
            ctx.context.equipment = [str(v) for v in value]
        else:
            raise ValueError("equipment must be a string or list")
    else:
        setattr(ctx.context, key, value)
    return f"{key} updated"

