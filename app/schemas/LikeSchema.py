from pydantic import BaseModel

class LikeCreateSchema(BaseModel):
    post_id: int
    likes_count: int

class LikeStateSchema(BaseModel):
    post_id: int
    likes_count: int
    liked_by_me: bool