from pydantic import BaseModel

class ResetMemoryRequest(BaseModel):
    thread_id: str
