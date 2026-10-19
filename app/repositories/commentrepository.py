from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.models.authmodel import User
from app.models.commentmodel import Comment



class CommentRepository:
    def __init__(self, db: AsyncSession)->None:
        self.db = db

    async def add_comment(self,comment:Comment)->Comment:
        self.db.add(comment)
        return comment

    async def get_by_id(self, comment_id: int)->Comment | None:
        return await self.db.get(Comment, comment_id) 

    async def get_by_post_id(self, post_id: int, limit=20, offset=0)->list[Comment]:
        rows = (await self.db.execute(
                    select(Comment, User.user_name)
                    .join(User, User.user_id == Comment.user_id)
                    .where(Comment.post_id == post_id)
                    .order_by(Comment.created_at.asc())
                    .limit(limit).offset(offset)
                )).all()

        for comment, user_name in rows:
            comment.user_name = user_name
        return [comment for comment, _ in rows]

    async def count_by_post_id(self, post_id: int)->int:
        stmt = select(func.count()).select_from(Comment).where(Comment.post_id == post_id)
        return await self.db.scalar(stmt) or 0

    async def delete(self, comment: Comment) -> None:
        await self.db.delete(comment)