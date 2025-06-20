import chromadb
from chromadb.utils import embedding_functions
from vector_store.embedder import get_embedding

def query_vector_db(query_text: str, top_k: int = 3):
    embedding = get_embedding(query_text)
    print("🔍 Querying:", query_text)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    print("✅ Results:", results)
    return results

chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="invoice_analysis")

def add_to_vector_db(document_id: str, text: str, metadata: dict):
    embedding = get_embedding(text)
    collection.add(
        ids=[document_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )

def query_vector_db(query_text: str, top_k: int = 3):
    embedding = get_embedding(query_text)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    return results
