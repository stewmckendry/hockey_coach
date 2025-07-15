import asyncio
import base64
from pathlib import Path

from agents import Agent, Runner, ImageGenerationTool
from agents.items import MessageOutputItem
from agents.items import ToolCallItem, ImageGenerationCall
import json

def fix_base64_padding(b64: str) -> str:
    return b64 + "=" * (-len(b64) % 4)

image_agent = Agent(
    name="image_generator",
    instructions="Generate a dryland hockey training visual for kids using the image_generation tool.",
    tools=[ImageGenerationTool(tool_config={"type": "image_generation", "quality": "low", "size": "1024x1024"})],
)

async def run():
    print("🚀 Running image generation agent...")
    res = await Runner.run(image_agent, "Generate a colorful off-ice hockey workout image for kids")

    output_dir = Path("test_outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    for item in res.new_items:
        if isinstance(item, ToolCallItem) and isinstance(item.raw_item, ImageGenerationCall):
            image_data_base64 = item.raw_item.result
            filename = output_dir / "off_ice_hockey_workout.png"
            with open(filename, "wb") as f:
                f.write(base64.b64decode(fix_base64_padding(image_data_base64)))
            print(f"📁 Saved image to {filename}")
        else:
            item_dict = {k: (str(v)[:200] if not isinstance(v, (str, int, float, bool, list, dict, type(None))) else (v[:200] if isinstance(v, str) else v))
                         for k, v in item.__dict__.items()}
            print(f"📝 Full item JSON: {json.dumps(item_dict, indent=2)}")



if __name__ == "__main__":
    asyncio.run(run())
