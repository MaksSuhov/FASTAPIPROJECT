from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.database.database import AsyncSessionLocal
from app.repositories.authreposiory import AuthRepository
from app.repositories.postrepository import PostRepository
from app.schemas.postschemas import PostCreateSchema, PostUpdateSchema
from app.services.postservice import PostService




class McpServise:
    def __init__(self,session_factory: async_sessionmaker[AsyncSession],
                 )->None:
        self.session_factory = session_factory

    async def get_profile(self, user_id:int)->dict:
        async with self.session_factory() as db_session:
            user = await AuthRepository(db_session).get_by_id(user_id)
        
            if user is None:
             return {'error': 'пользователь не найден'}
            return {
                'user_id':user.user_id,
                'user_name': user.user_name,
                'roles': [role.role_name for role in user.roles],
                'created_at': user.created_at.isoformat()
                if user.created_at
                  else None
            }
    async def get_posts(self, user_id: int)->dict:
        async with self.session_factory() as db_session:
            user = await AuthRepository(db_session).get_by_id(user_id=user_id)

            if user is None:
                return {'error': 'Пользователь не найден'}

            try:
                posts = await PostRepository(db_session).get_by_user_id(user_id)
            except:
                return {'user_id':user_id,
                        'posts_count': 0,
                        'posts': [],
                        'error': 'Не удалось найти посты пользователя'
                        }
            formatted_posts = [
                {
                'post_id': post.post_id,
                'title': post.title,
                'created_at': post.created_at
                }
                for post in posts
            ]   
            return {
                'user_id': user_id,
                'posts_count': len(formatted_posts),
                'posts':formatted_posts
            }

    async def create_post(self, user_id:int, title:str, content:str)->dict:    

        async with self.session_factory() as db_session:
            user = await AuthRepository(db_session).get_by_id(user_id)

            if user is None:
                return {'error': 'пользователь не найден'}

            post = await PostService(db_session, user).create_post(PostCreateSchema(title=title, content=content))

            return {
                'post_id': post.post_id,
                'title': post.title,
                'content': post.content,
                'author_id': post.author_id,
                'created_at': post.created_at.isoformat()
                if post.created_at
                else None    
            }

    async def update_post(self, post_id:int,
                          user_id:int,
                          title: str | None = None,
                          content: str | None = None)->dict:
        async with self.session_factory() as db_session:
            user = await AuthRepository(db_session).get_by_id(user_id)

            if user is None:
                  return {'error': 'пользователь не найден'}
            
            post = await PostRepository(db_session).get_by_id(post_id)

            if post is None:
                 return {'error': 'пост не найден'}

            if post.author_id != user.user_id:
                return {'error': 'не достаточно прав для редактирования'}

            data = {k:v for k,v in {'title':title, 'content':content}.items() if v is not None}
            if not data:
                return {'error':'нечего обновлять'}

            updated = await PostService(db_session, user).update_post(post_id, PostUpdateSchema(**data))

            return {
                'post_id': updated.post_id,
                'title': updated.title,
                'content': updated.content,
                'author_id': updated.author_id
            }

    async def delete_post(self, user_id:int,post_id:int)->dict:
        async with self.session_factory() as db_session:
            user = await AuthRepository(db_session).get_by_id(user_id)
                
            if user is None:
                return {'error': 'пользователь не найден'}
                            
            try:
                await PostService(db_session, user).delete(post_id=post_id)
            except HTTPException as exc:
                return {'error': exc.detail or 'недостаточно прав для удаления'}

            return {"post_id": post_id, "status": "deleted"}