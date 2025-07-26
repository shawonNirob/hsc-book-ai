from pydantic import BaseModel

class AskRequest(BaseModel):
    query: str
    thread_id: str
