from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models.authmodel import User
from app.models.postmodel import Post
from app.repositories.postrepository import PostRepository
from app.schemas.postschemas import PostUpdateSchema



class AdminService:
    def __init__(self,db:AsyncSession, current_user:User)->None:
        self.db = db
        self.current_user = current_user
        self.post_repository = PostRepository(db)

    async def admin_update(
            self,
            post_id: int,
            payload: PostUpdateSchema,
            ) -> Post:
        db_post = await self.db.get(Post, post_id)
        if db_post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

        updated_post = payload.model_dump(exclude_unset=True)
        for k, v in updated_post.items():
            setattr(db_post, k, v)

        await self.db.commit()
        await self.db.refresh(db_post)
        return db_post

    async def admin_delete(self, post_id:int)->None:
        post_to_delete = await self.db.get(Post, post_id)

        if not post_to_delete:
            raise HTTPException(status_code=404, detail="Пост не найден")

        await self.post_repository.delete(post_id)
        await self.db.commit()


