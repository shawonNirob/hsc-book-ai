from pydantic import BaseModel

class CosineRequest(BaseModel):
    query: str