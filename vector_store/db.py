import chromadb
from chromadb.utils import embedding_functions
from vector_store.embedder import get_embedding


chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="invoice_analysis")

def add_to_vector_db(document_id: str, text: str, metadata: dict):
    """
    Add a document and its metadata + embedding to the vector store.
    """
    embedding = get_embedding(text)
    collection.add(
        ids=[document_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )

def query_vector_db(query_text: str, top_k: int = 3, filters: dict = None):
    """
    Query ChromaDB with embedding similarity.
    Filters are applied manually in Python.
    """
    embedding = get_embedding(query_text)


    raw_results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k * 5  
    )

    filtered = []
    for i in range(len(raw_results["documents"][0])):
        meta = raw_results["metadatas"][0][i]
        if not filters or all(meta.get(k) == v for k, v in filters.items()):
            filtered.append({
                "text": raw_results["documents"][0][i],
                "metadata": meta,
                "id": raw_results["ids"][0][i]
            })
        if len(filtered) >= top_k:
            break

    return {
        "documents": [[doc["text"] for doc in filtered]],
        "metadatas": [[doc["metadata"] for doc in filtered]],
        "ids": [[doc["id"] for doc in filtered]]
    }


def search_similar_docs(query: str, top_k: int = 5):
    """
    Perform vector search and return a list of documents with metadata.
    """
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
