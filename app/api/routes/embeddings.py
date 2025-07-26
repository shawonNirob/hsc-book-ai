from fastapi import APIRouter, File, UploadFile, HTTPException
from app.qdrant.pdf_clean import process_pdf_semantically
from app.qdrant.insert_vector import insert_chunks_to_qdrant
from typing import Dict, Any
import logging
from app.qdrant.vector_search import search_documents
from loguru import logger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/insert-vector", response_model=Dict[str, Any], status_code=200)
async def upload_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        chunks = process_pdf_semantically(contents)
        insert_chunks_to_qdrant(chunks)

        return {"message": f"Inserted {len(chunks)} chunks from PDF into Qdrant."}
    
    except Exception as e:
        logger.error(f"Error in insert_vector: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Vector insertion failed: {str(e)}")
    

@router.post("/search_vector", response_model=Dict[str, Any], status_code=200)
def search_vector(request: str) -> Dict[str, Any]:
    try:
        logger.info(f"Received search request with query: {request}")
        results = search_documents(request)
        logger.info(f"Found {len(results)} results")
        return {"results": results}

    except Exception as e:
        logger.error(f"Error in search_vector: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")