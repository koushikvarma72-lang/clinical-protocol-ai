import chromadb
from chromadb.config import Settings

def get_collection():
    client = chromadb.PersistentClient(
        path="chroma_db",   # ← this WILL create folder
        settings=Settings(
            anonymized_telemetry=False
        )
    )

    collection = client.get_or_create_collection(
        name="clinical_protocol",
        metadata={"hnsw:space": "cosine"}  # Use cosine similarity instead of L2
    )

    return collection
