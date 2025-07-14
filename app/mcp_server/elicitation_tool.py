from __future__ import annotations

"""FastMCP tool demonstrating the `ctx.elicit` flow."""

from typing import Literal

from fastmcp import FastMCP, Context


mcp = FastMCP("Thunder Elicitation Server")


@mcp.tool(title="Choose Skill Focus")
async def choose_skill_focus(ctx: Context) -> str:
    """Ask the user to choose a skill focus area."""
    result = await ctx.elicit(
        message="Which skill do you want to focus on?",
        response_type=Literal["Skating", "Passing", "Backchecking", "Shooting"],
    )

    if result.action == "accept":
        return f"Great choice! We'll focus on {result.data}."
    elif result.action == "decline":
        return "No skill selected."
    else:
        return "Operation cancelled."
