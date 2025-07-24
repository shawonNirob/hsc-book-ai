from qdrant.model import embedding_model
from app.qdrant.qdrant_connect import client

COLLECTION_NAME = "hsc_book"

def search_documents(query):
    query_vector = embedding_model.embed_query(query)
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=5
    )

    results = []
    for hit in search_result:
        results.append({
            "text": hit.payload["text"],
            "page": hit.payload["page"],
            "score": hit.score
        })

    return {"query": query, "results": results}
