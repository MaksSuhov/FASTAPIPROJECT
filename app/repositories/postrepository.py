from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postmodel import Post
from app.schemas.postschemas import PostCreateSchema


class PostRepository:
    def __init__(self, db: AsyncSession)->None:
        self.db = db

    async def get_all(self)->list[Post]:
        all_post = await self.db.scalars(select(Post))
        return all_post.all()

    async def get_by_id(self, post_id:int)->Post | None:
        return await self.db.get(Post, post_id)

    async def save(self, payload:PostCreateSchema)->Post:
       return self.db.add(payload)

    async def delete(self, post_id:int)->None:
        post_to_delete = await self.db.get(Post, post_id)
        return await self.db.delete(post_to_delete)

