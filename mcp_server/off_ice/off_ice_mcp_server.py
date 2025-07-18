import logging
import os
from typing import Dict, List, Any

from fastmcp import FastMCP
from openai import OpenAI
from chroma_utils import get_chroma_collection
from datetime_tools import get_current_date

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Env config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID", "")

client = OpenAI()
collection = get_chroma_collection()

server_instructions = """
This MCP server provides dryland training search tools for youth hockey coaches.
Use the search tool to locate appropriate exercises or videos from Hockey Canada guidance,
and use fetch to retrieve full content for context and citation.
"""

def create_server():
    mcp = FastMCP(name="Dryland MCP Server", instructions=server_instructions)

    mcp.description = "Off-ice hockey training assistant for drills and video clips."
    mcp.version = "v1.0.0"
    mcp.id = "dryland-mcp-server"
    mcp.contact = {"name": "Stewart McKendry", "email": "your@email.com"}
    mcp.license = {"name": "MIT", "url": "https://opensource.org/licenses/MIT"}

    #mcp.tool(get_current_date)

    @mcp.tool(name="search")
    async def search(query: str) -> Dict[str, List[Dict[str, Any]]]:
        logger.info(f"Searching drills and videos for: {query}")

        results = collection.query(
            query_texts=[query],
            n_results=10,
            where={"$or": [
                {"source": "off_ice_manual_hockey_canada_level1"},
                {"type": "off_ice_video"}
            ]},
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        ids = results.get("ids", [[]])[0]

        entries = []
        for doc, meta, uid in zip(docs, metas, ids):
            is_video = meta.get("type") == "off_ice_video"
            entry_id = f"video:{uid}" if is_video else f"drill:{uid}"
            title = meta.get("title", "Untitled")
            text = extract_description(doc)
            url = meta.get("video_url") if is_video else f"https://your.site/drill/{uid}"

            entries.append({
                "id": entry_id,
                "title": title,
                "text": text[:200] + "..." if len(text) > 200 else text,
                "url": url or "https://your.site"
            })

        return {"results": entries}

    @mcp.tool(name="fetch")
    async def fetch(id: str) -> Dict[str, Any]:
        logger.info(f"Fetching item: {id}")

        if id.startswith("drill:"):
            raw_id = id.replace("drill:", "")
            where_clause = {"source": "off_ice_manual_hockey_canada_level1"}
        elif id.startswith("video:"):
            raw_id = id.replace("video:", "")
            where_clause = {"type": "off_ice_video"}
        else:
            raise ValueError("Invalid ID prefix")

        data = collection.get(ids=[raw_id], where=where_clause, include=["documents", "metadatas"])
        docs = data.get("documents", [""])
        metas = data.get("metadatas", [{}])

        if not docs or not metas:
            raise ValueError(f"Item not found for ID: {id}")

        doc = docs[0]
        meta = metas[0]
        is_video = id.startswith("video:")
        title = meta.get("title", "Untitled")
        url = meta.get("video_url") if is_video else f"https://your.site/drill/{raw_id}"

        return {
            "id": id,
            "title": title,
            "text": doc,
            "url": url or "https://your.site",
            "metadata": meta
        }

    return mcp

def extract_description(doc: str) -> str:
    for line in doc.splitlines():
        if line.lower().startswith("description:"):
            return line.split(":", 1)[1].strip()
    return doc[:300]

def main():
    logger.info("Starting Dryland MCP Server")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY must be set")

    server = create_server()
    server.run(transport="sse", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
