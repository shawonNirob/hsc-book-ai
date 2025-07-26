from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.chat import router as chat_router
from app.api.routes.embeddings import router as embedding_router
from app.api.routes.matrix_evaluation import router as matrix_router

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/agent", tags=["chat"])
app.include_router(embedding_router, prefix="/embeddings", tags=["embedding"])
app.include_router(matrix_router, prefix="/matrix-evaluation", tags=["similarity"])

@app.get("/")
def read_root():
    return {"message": "Welcome to HSC BOOK AI"}

@app.get("/_status")
def read_status():
    return {"status": "ok"}





