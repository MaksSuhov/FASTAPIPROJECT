
from pydantic import BaseModel, Field



class ChatRequest(BaseModel):
    conversation_id: int | None = Field(default=None, gt=0)
    content: str = Field(min_length=1, max_length=4000)
