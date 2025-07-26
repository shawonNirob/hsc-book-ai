from langchain_community.vectorstores import Qdrant
from app.qdrant.model import embedding_model
from qdrant_client.models import PointStruct, Distance, VectorParams
import uuid
from app.qdrant.qdrant_connect import client
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


COLLECTION_NAME = "hsc_book"

def create_collection_if_not_exists():
    try:
        client.get_collection(COLLECTION_NAME)
    except Exception as e:
        logger.info(f"Collection {COLLECTION_NAME} does not exist. Creating new collection.")
        try:
            client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            logger.info(f"Collection {COLLECTION_NAME} created.")
        except Exception as ce:
            logger.error(f"Error creating collection: {ce}", exc_info=True)
            raise

def insert_chunks_to_qdrant(chunks: list[dict]):

    if not chunks:
        logger.warning("No chunks provided for insertion. Aborting.")
        return

    try:
        create_collection_if_not_exists()

        points_to_upsert = []
        texts_to_embed = []

        for chunk in chunks:
            if chunk['content_type'] == 'mcq':
                text_for_embedding = chunk.get('question_text', '')
            elif chunk['content_type'] == 'creative_question':
                text_for_embedding = chunk.get('full_text', '')
            else: 
                text_for_embedding = chunk.get('text', '')

            texts_to_embed.append(text_for_embedding)

        logger.info(f"Embedding {len(texts_to_embed)} text chunks...")
        vectors = embedding_model.embed_documents(texts_to_embed)
        logger.info("Embedding completed.")

        for i, chunk in enumerate(chunks):
            payload = chunk.copy()
            points_to_upsert.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vectors[i],
                    payload=payload
                )
            )
            
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points_to_upsert,
            wait=True
        )
        logger.info(f"Inserted {len(points_to_upsert)} points into collection '{COLLECTION_NAME}'.")

    except Exception as e:
        logger.error(f"Error inserting data into Qdrant: {e}", exc_info=True)
        raise

