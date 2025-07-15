from fastmcp import FastMCP
from fastmcp import Context  # context type imported here
from typing import Literal

mcp = FastMCP(name="Sample")

@mcp.tool(name="Choose_Skill_Focus")
async def choose_skill_focus(ctx: Context) -> str:
    try:
        result = await ctx.elicit(
            message="Which skill do you want to focus on?",
            response_type=Literal["Skating", "Passing", "Backchecking", "Shooting"]
        )
    except Exception as e:
        print("❌ Elicitation failed:", e)
        raise

    return f"✅ Got: {result.data}" if result.action == "accept" else "No selection"

if __name__ == "__main__":
    mcp.run(transport="sse")  # defaults to /sse endpoint
