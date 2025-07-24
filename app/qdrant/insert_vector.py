from langchain.vectorstores import Qdrant 
from app.qdrant.model import embedding_model
from qdrant_client.models import PointStruct, Distance, VectorParams
import uuid
from app.qdrant.qdrant_connect import client


COLLECTION_NAME = "hsc_book"

def create_collection_if_not_exists():
    try:
        client.get_collection(COLLECTION_NAME)
    except:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vector_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

def insert_documents_to_qdrant(chunks):
    create_collection_if_not_exists()
    documents = [chunk["text"] for chunk in chunks]
    vectors = embedding_model.embed_documents(documents)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"text": text, "page": chunk["page"]}
        )
        for vector, text, chunk in zip(vectors, documents, chunks)
    ]

    client.upsert(collection_name=COLLECTION_NAME, points=points)
