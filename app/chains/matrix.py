from app.qdrant.vector_search import search_documents

def get_cosine_similarity(query: str) -> dict:
    if not query or not query.strip():
        return {"error": "Query is empty."}

    result = search_documents(query)
    return result
