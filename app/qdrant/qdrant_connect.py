import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from qdrant_client import QdrantClient
from app.config import settings

client = QdrantClient(
    url="https://2a964a00-5b72-4b2c-84b2-9afb20f59a30.us-east-1-0.aws.cloud.qdrant.io:6333", 
    api_key=settings.QDRANT_API_KEY,
    timeout=1000.0
)
logger.info("QdrantClient instance created.")
