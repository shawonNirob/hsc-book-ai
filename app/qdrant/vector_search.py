import logging
from app.qdrant.model import embedding_model
from app.qdrant.qdrant_connect import client

COLLECTION_NAME = "hsc_book"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_documents(query: str, limit: int = 5):

    logger.info(f"Searching for query: '{query}'")
    try:
        query_vector = embedding_model.embed_query(query)
        
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            with_payload=True 
        )

        results = []
        for hit in search_result:
            result_item = hit.payload
            result_item['score'] = hit.score
            results.append(result_item)
            
        logger.info(f"Found {len(results)} results.")
        return {"query": query, "results": results}

    except Exception as e:
        logger.error(f"Error during document search: {e}", exc_info=True)
        return {"query": query, "results": [], "error": str(e)}
