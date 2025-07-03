# chroma_utils.py
import os
from pathlib import Path
import chromadb
from chromadb.api import ClientAPI
from chromadb.api.types import Documents, Embeddings, IDs, Metadatas
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from dotenv import load_dotenv
load_dotenv()

COLLECTION_NAME = "hockey_drills"
_embed = OpenAIEmbeddingFunction(api_key=os.getenv("OPENAI_API_KEY"))

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

def clear_chroma_collection():
    """Delete all documents in the Chroma collection by ID."""
    collection = get_chroma_collection()
    try:
        results = collection.get()  # No 'include' needed; ids are always returned
        ids = results.get("ids", [])
        if ids:
            collection.delete(ids=ids)
            print(f"🧹 Cleared {len(ids)} documents from Chroma collection.")
        else:
            print("✅ Chroma collection is already empty.")
    except Exception as e:
        print(f"❌ Failed to clear Chroma collection: {e}")


