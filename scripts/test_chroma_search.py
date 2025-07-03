import sys
from pathlib import Path
from typing import List, Dict
import os

sys.path.append(str(Path(__file__).parent.parent / "mcp_server"))
from chroma_utils import get_chroma_collection
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from dotenv import load_dotenv
load_dotenv()


query_text = "skating backcheck"
n_results = 5

collection = get_chroma_collection()
results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
    )

docs = results.get("documents", [[]])[0]
metas = results.get("metadatas", [[]])[0]
records: List[Dict] = []
for doc, meta in zip(docs, metas):
    record = {"text": doc}
    if isinstance(meta, dict):
        record.update(meta)
    records.append(record)

print("📦 Total documents in collection:", collection.count())
print("Results:", records)