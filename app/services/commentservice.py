from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models.authmodel import User
from app.models.commentmodel import Comment
from app.models.postmodel import Post
from app.repositories.commentrepository import CommentRepository
from app.repositories.postrepository import PostRepository
from app.schemas.commentschema import CommentCreateSchema

class CommentService:
    def __init__(self, db: AsyncSession, current_user: User | None)->None:
        self.db = db
        self.current_user = current_user
        self.post_repository = PostRepository(db)
        self.comment_repository = CommentRepository(db)

    async def _get_post_or_404(self, post_id: int)-> Post:
        post = await self.post_repository.get_by_id(post_id)
        if post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return post

    def _require_user(self) -> User:
        if self.current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='необходимо авторизоваться',
            )
        return self.current_user

    async def get_comments(self, post_id:int, limit = 20, offset = 0)->list[Comment]:
        await self._get_post_or_404(post_id)
        return await self.comment_repository.get_by_post_id(post_id, limit, offset)

    async def add_comment(self, post_id:int, payload: CommentCreateSchema)->Comment:
        post_for_comment = await self._get_post_or_404(post_id)

        author = self._require_user()
        comment = Comment(
            user_id = author.user_id,
            post_id = post_for_comment.post_id,
            content = payload.content
        )

        await self.comment_repository.add_comment(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        comment.user_name = author.user_name
        return comment

    async def delete_comment(self, post_id: int, comment_id:int)->None:
        comment = await self.comment_repository.get_by_id(comment_id)
        author = self._require_user()
        if comment is None or comment.post_id != post_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='недостаточно прав')
        if comment.user_id != author.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='недостаточно прав')
        await self.comment_repository.delete(comment)
        await self.db.commit()

    