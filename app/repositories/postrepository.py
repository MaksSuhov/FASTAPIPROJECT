from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.authmodel import User
from app.models.commentmodel import Comment
from app.models.likesmodel import Like
from app.models.postmodel import Post
from app.schemas.postschemas import PostCreateSchema


class PostRepository:
    def __init__(self, db: AsyncSession)->None:
        self.db = db

    async def get_all(self, limit: int = 20, offset: int = 0, viewer_id: int | None = None)->list[Post]:
        viewer_id = viewer_id if viewer_id is not None else 0

        name_subq = (select(User.user_name)
             .where(User.user_id == Post.author_id)
             .scalar_subquery()
             .label('author_username'))

        comments_subq = (select(func.count(Comment.comment_id))
                        .where(Comment.post_id == Post.post_id)
                        .scalar_subquery()
                        .label('comments_count'))

        stmt = (select(Post, comments_subq, name_subq, func.count(Like.user_id).label('likes_count'),func.count(case((Like.user_id == viewer_id, 1))).label('liked_by_me'))
                .outerjoin(Like, Like.post_id == Post.post_id)
                .group_by(Post.post_id)
                .order_by(Post.created_at.desc())
                .limit(limit)
                .offset(offset))
        rows = (await self.db.execute(stmt)).all()

        posts = []
        for post,comments_count, author_username, likes_count, liked_by_me in rows:
            post.author_username = author_username
            post.comments_count = comments_count
            post.likes_count = likes_count
            post.liked_by_me = bool(liked_by_me)
            posts.append(post)
        return list(posts)

        

    async def get_by_id(self, post_id:int)->Post | None:
        return await self.db.get(Post, post_id)

    async def get_by_user_id(self, user_id: int)->list[Post]:
        return await self.db.scalars(select(Post).where(Post.author_id == user_id))

    async def save(self, payload:PostCreateSchema)->Post:
       return self.db.add(payload)

    async def delete(self, post_id:int)->None:
        post_to_delete = await self.db.get(Post, post_id)
        return await self.db.delete(post_to_delete)

