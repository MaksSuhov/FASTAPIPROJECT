from fastapi import  HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models.authmodel import User
from app.models.postmodel import Post
from app.repositories.authreposiory import AuthRepository
from app.repositories.postrepository import PostRepository
from app.schemas.postschemas import PostCreateSchema, PostUpdateSchema


class PostService:
    def __init__(self, db:AsyncSession, current_user:User)->None:
        self.db = db
        self.current_user = current_user
        self.post_repository = PostRepository(db)
        self.auth_repository = AuthRepository(db)

    async def get_all(self)->list[Post]:
        return await self.post_repository.get_all()

    async def create_post(
            self,
            payload: PostCreateSchema
            )-> Post:

        new_post = Post(
            title=payload.title,
            content=payload.content,
            author_id=self.current_user.user_id
        )

        await self.post_repository.save(new_post)
        await self.db.commit()
        await self.db.refresh(new_post)
        return new_post

    async def update_post(
            self,
            post_id: int,
            payload:PostUpdateSchema
    )->Post:

        db_post = await self.post_repository.get_by_id(post_id)
        if not db_post:
            raise HTTPException(status_code=404, detail="Пост не найден")

        if db_post.author_id != self.current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для редактирования этого поста"
            )

        updated_post = payload.model_dump(exclude_unset=True)
        for k, v in updated_post.items():
            setattr(db_post, k, v)

        await self.db.commit()
        await self.db.refresh(db_post)
        return db_post

    async def delete(
            self,
            post_id: int,
    ) -> None:
        post_to_delete =await self.post_repository.get_by_id(post_id)

        if not post_to_delete:
            raise HTTPException(status_code=404, detail="Пост не найден")

        if post_to_delete.author_id != self.current_user.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        await self.post_repository.delete(post_id)
        await self.db.commit()

