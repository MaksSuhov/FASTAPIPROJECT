from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.likesmodel import Like






class LikeRepository():
    def __init__(self, db: AsyncSession):
        self.db = db

    async def count_by_post_id(self, post_id: int)->int:
        stmt = select(func.count()).select_from(Like).where(Like.post_id == post_id)
        return await self.db.scalar(stmt) or 0

    async def exists(self, post_id: int, user_id: int)->bool:
        stmt = select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
        return await self.db.scalar(stmt) is not None

    async def add_like(self,like: Like)->Like:
       self.db.add(like)
       return like
        
    async def delete_like(self, post_id: int, user_id: int)->None:
        like_to_delete = await self.db.get(Like, (user_id, post_id))
        if like_to_delete is not None:
            await self.db.delete(like_to_delete)
