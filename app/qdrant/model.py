from langchain_community.embeddings import OpenAIEmbeddings
from app.config import settings
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
logger.info("Initializing OpenAI Embeddings model.")
embedding_model = OpenAIEmbeddings(
    model = settings.EMBEDDING_MODEL,
    dimensions = 1536
)