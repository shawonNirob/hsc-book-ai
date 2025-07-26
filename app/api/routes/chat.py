from fastapi import APIRouter, HTTPException
from app.schemas.chat_schema import AskRequest
import logging
from typing import Dict, Any
from app.chains.llm_chain import process_query
from app.chains.llm_chain import reset_conversation_memory
from app.schemas.memory_schema import ResetMemoryRequest


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

QUERY_CHAR_LIMIT = 5000

@router.post("/ask", response_model=Dict[str, Any], status_code=200)
def ask(request: AskRequest) -> Dict[str, Any]:
    if len(request.query) > QUERY_CHAR_LIMIT:
        return {"error": "Query size exceeded", "allowed_limit": QUERY_CHAR_LIMIT}

    try:
        logger.info(f"Received ask request with query: {request.query} and thread_id: {request.thread_id}")
        return process_query(request.query, thread_id=request.thread_id)
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset_memory")
def reset_memory_json(request_data: ResetMemoryRequest) -> Dict[str, str]:
    thread_id = request_data.thread_id

    try:
        logger.info(f"Resetting memory for thread_id: {thread_id}")
        result = reset_conversation_memory(thread_id)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return result

    except Exception as e:
        logger.error(f"Error in reset_memory_json endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
