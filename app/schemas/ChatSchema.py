
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    conversation_id: int | None = Field(default=None, gt=0)
    content: str = Field(min_length=1, max_length=4000)

class ChatMessageSchema(BaseModel):
    conversation_id: int
    message_id:int
    content: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationSchema(BaseModel):
    conversation_id: int
    user_id: int
    created_at: datetime
    title: str | None = None
    messages: list[ChatMessageSchema] = []

    model_config = ConfigDict(from_attributes=True)