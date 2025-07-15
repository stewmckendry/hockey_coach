import asyncio
from pydantic import BaseModel, Field
from agents import Agent, Runner
from agents.mcp import MCPServerSse, MCPServerSseParams
from fastmcp.client.elicitation import ElicitResult

# Strict input schema for tools if needed (not mandatory here)
class DummyInput(BaseModel):
    prompt: str = Field(...)

async def main():
    # Initialize MCP server client wrapper
    mcp_server = MCPServerSse(
        params=MCPServerSseParams(
            url="http://localhost:8000/sse",
            capabilities={"elicitation": {}}
        )
    )
    await mcp_server.connect()
    # Create your agent with MCP server
    agent = Agent(
        name="PracticeCoach",
        instructions="""
            You are a youth hockey assistant helping a coach prepare for practice.
            Use the MCP tools to ask which skill to focus on, then provide a drill suggestion.
            """,
        mcp_servers=[mcp_server],
    )

    # Run agent interaction
    result = await Runner.run(agent, "Plan a practice session")
    print("\n✅ Agent Output:\n", result.final_output)

    await mcp_server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
