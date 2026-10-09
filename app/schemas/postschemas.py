from pydantic import BaseModel, ConfigDict, Field


class PostSchema(BaseModel):
    post_id: int
    title: str
    content: str
    author_id: int

    model_config = ConfigDict(from_attributes=True)

class PostCreateSchema(BaseModel):
    title:str = Field(min_length=1, max_length=100)
    content:str = Field(min_length=1, max_length=4000)

class PostUpdateSchema(BaseModel):
    title:str | None = Field(default=None, min_length=1, max_length=100)
    content:str | None = Field(default=None, min_length=1, max_length=4000)
