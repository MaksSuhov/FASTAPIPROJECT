from pydantic import BaseModel, ConfigDict


class PostSchema(BaseModel):
    post_id: int
    title: str
    content: str
    author_id: int

    model_config = ConfigDict(from_attributes=True)

class PostCreateSchema(BaseModel):
    title:str
    content:str

class PostUpdateSchema(BaseModel):
    title:str | None = None
    content:str | None = None
