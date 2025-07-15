from typing import Any
import asyncio
from pprint import pprint
from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult

async def basic_elicitation_handler(message, response_type, params, context):
    options = params.get("options", []) if isinstance(params, dict) else []
    print(f"{message}")
    if options:
        print("Options:", ", ".join(options))

    user_input = input("Your response: ").strip().title()
    return response_type(value=user_input)


async def run_demo():
    async with Client("http://localhost:8000/sse", elicitation_handler=basic_elicitation_handler) as client:
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])  # expects 'Choose Skill Focus'
        result = await client.call_tool("Choose Skill Focus", {})
        print("✅ Final Output:")
        pprint(result.data or result.content[0].text or result)


def main():
    asyncio.run(run_demo())

if __name__ == "__main__":
    main()




