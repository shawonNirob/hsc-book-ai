from langchain.embeddings import OpenAIEmbeddings
from app.config import settings
import os

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

embedding_model = OpenAIEmbeddings(
    model = settings.EMBEDDING_MODEL,
    dimensions = 1536
)