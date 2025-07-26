from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging
from app.chains.matrix import get_cosine_similarity
from app.schemas.cosine_schema import CosineRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/cosine-similarity", response_model=Dict[str, Any], status_code=200)
def cosine_similarity(request: CosineRequest) -> Dict[str, Any]:
    try:
        logger.info(f"Received cosine similarity request: {request.query}")
        result = get_cosine_similarity(request.query)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except Exception as e:
        logger.error(f"Error in cosine_similarity endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")

    

