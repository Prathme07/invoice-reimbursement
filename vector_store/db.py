import chromadb
from chromadb.utils import embedding_functions
from vector_store.embedder import get_embedding


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

# Basic query
def query_vector_db(query_text: str, top_k: int = 3):
    embedding = get_embedding(query_text)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    return results

def search_similar_docs(query: str, top_k: int = 5):
    embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    docs = []
    for i in range(len(results["documents"][0])):
        docs.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "id": results["ids"][0][i]
        })
    return docs
