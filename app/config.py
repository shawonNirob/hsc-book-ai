from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    MODEL_ID: str
    QDRANT_API_KEY: str 
    EMBEDDING_MODEL: str

    class Config:
        env_file = ".env"

settings = Settings()

