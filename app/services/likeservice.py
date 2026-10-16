from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.authmodel import User
from app.models.likesmodel import Like
from app.models.postmodel import Post
from app.repositories.authreposiory import AuthRepository
from app.repositories.likerepository import LikeRepository
from app.repositories.postrepository import PostRepository






class LikeService:
    def __init__(self, db: AsyncSession, current_user: User):
        self.db = db
        self.current_user = current_user
        self.like_repository = LikeRepository(db)
        self.post_repository = PostRepository(db)

    async def _get_post_or_404(self, post_id: int) -> Post:
        post = await self.post_repository.get_by_id(post_id)
        if post is None:
            raise HTTPException(status_code=404, detail='Пост не найден')
        return post

    async def get_state(self, post_id: int) -> dict:
        return {
            'post_id': post_id,
            'likes_count': await self.like_repository.count_by_post_id(post_id),
            'liked_by_me': await self.like_repository.exists(post_id, self.current_user.user_id),
        }

    async def add_like(self, post_id:int)->dict:
        await self._get_post_or_404(post_id)

        already_liked = await self.like_repository.exists(post_id=post_id, user_id=self.current_user.user_id)

        if not already_liked:
            new_like = Like(
                user_id= self.current_user.user_id,
                post_id=post_id,
            )

            await self.like_repository.add_like(new_like)
            await self.db.commit()
        return await self.get_state(post_id)

    async def delete_like(self, post_id: id)->dict:
        await self._get_post_or_404(post_id)

        await self.like_repository.delete_like(post_id, self.current_user.user_id)
        await self.db.commit()
        return await self.get_state(post_id)
    
                
        