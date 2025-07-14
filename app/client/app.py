from __future__ import annotations

"""CLI demo that interacts with the elicitation tool."""

import asyncio
import subprocess
import time
from typing import Any

from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult


async def basic_elicitation_handler(
    message: str, response_type: type, params: Any, context: Any
) -> Any:
    """Simple handler that collects user input from the console."""
    print(f"\n🧠 Server asks: {message}")
    user_response = input("📝 Your response: ").strip()

    if not user_response:
        return ElicitResult(action="decline")

    return response_type(value=user_response)


async def run_demo() -> None:
    client = Client(
        "http://localhost:8000",
        elicitation_handler=basic_elicitation_handler,
    )

    response = await client.invoke("Choose Skill Focus")
    print(f"\n✅ Final Output: {response.output}")


def main() -> None:
    proc = subprocess.Popen(["uvicorn", "app.mcp_server.toolserver:app"])
    time.sleep(1)

    try:
        asyncio.run(run_demo())
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
