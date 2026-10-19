from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field



class CommentCreateSchema(BaseModel):
    content: str = Field(min_length=1, max_length=200)

class CommenUpdateSchema(BaseModel):
    content: str = Field(min_length=1, max_length=200)    

class CommentSchema(BaseModel):

    comment_id: int
    post_id: int
    user_id: int
    user_name: str | None = None
    content: str 
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)