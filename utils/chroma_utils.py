# chroma_utils.py
import os
from pathlib import Path
import logging
import chromadb
from chromadb.api import ClientAPI
from chromadb.api.types import Documents, Embeddings, IDs, Metadatas
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from dotenv import load_dotenv
load_dotenv()

COLLECTION_NAME = "hockey_drills"
_embed = OpenAIEmbeddingFunction(api_key=os.getenv("OPENAI_API_KEY"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_client() -> ClientAPI:
    host = os.getenv("CHROMA_SERVER_HOST", "localhost")
    port = int(os.getenv("CHROMA_SERVER_HTTP_PORT", "8000"))
    token = os.getenv("CHROMA_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else None
    print(f"Connecting to Chroma server at {host}:{port} with token: {bool(token)}")
    return chromadb.HttpClient(host=host, port=port, headers=headers)

def get_chroma_collection():
    client = get_client()
    print(f"Using Chroma client: {client}")
    collection = client.get_or_create_collection(COLLECTION_NAME, embedding_function=_embed)
    return collection

def clear_chroma_collection(
    mode: str = "all",
    prefix: str | None = None,
    ids: list[str] | None = None,
) -> None:
    """Delete documents from the Chroma collection.

    Modes:
        - "all": remove everything (default)
        - "type": remove docs with ID starting with ``prefix``
        - "ids": remove specific document IDs
    """
    collection = get_chroma_collection()
    try:
        all_ids = collection.get().get("ids", [])

        if mode == "ids":
            ids_to_delete = ids or []
        elif mode == "type":
            if not prefix:
                logger.warning("Prefix required for mode='type'. No documents deleted.")
                return
            ids_to_delete = [i for i in all_ids if str(i).startswith(prefix)]
        else:  # mode == "all" or unspecified
            ids_to_delete = all_ids

        if not ids_to_delete:
            logger.info("No matching documents to delete from Chroma collection.")
            return

        collection.delete(ids=ids_to_delete)
        logger.info(
            "🧹 Deleted %s documents from Chroma collection (%s mode)",
            len(ids_to_delete),
            mode,
        )
    except Exception as e:
        logger.error("❌ Failed to clear Chroma collection: %s", e)


