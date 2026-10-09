import logging
from typing import Any
from fastapi import Depends
from fastmcp import FastMCP


from app.database.database import AsyncSessionLocal
from app.repositories.postrepository import PostRepository
from app.schemas.postschemas import PostCreateSchema
from app.services.mcpservice import McpServise
from app.services.postservice import PostService


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

mcp = FastMCP('PRACTICESERVER')

mcp_service = McpServise(AsyncSessionLocal)


@mcp.tool
async def get_my_profile(user_id:int)->dict:
    """
    получить информацию о пользователе, user_id подставляется автоматически.
    """
    return await mcp_service.get_profile(user_id)
    

@mcp.tool()
async def get_user_posts(user_id: int) -> dict:
    """
        Асинхронно получить список постов пользователя из внутренней базы данных.

        args:
            user_id (int): Уникальный идентификатор пользователя.
        returns:
            dict: Словарь со списком заказов или сообщением об ошибке.
        """
    try:
        async with AsyncSessionLocal() as db_session:
            repo = PostRepository(db_session)
            posts = await repo.get_by_user_id(user_id=user_id)

            formatted_posts: list[dict[str, Any]] = [{
                'post_id': post.post_id,
                'title' : post.title,
                'created_at': post.created_at
             }
             for post in posts
            ]
            return{
                'user_id': user_id,
                'posts_count': len(formatted_posts),
                'posts': formatted_posts
            }
    except Exception as e:
        logger.error(f"Ошибка БД: {e}")
        return {
            "user_id": user_id,
            "posts_count": 0,
            "posts": [],
            "error": "Не удалось получить посты из базы данных",
        }

@mcp.tool()
async def mcp_create_post(user_id:int, title:str, content:str)->dict:
    """
    Создать пост от имени пользователя как с задным payload так и с наполнением от ассистента
    Его user_id подставляется в инструменты автоматически — не спрашивай его и не отказывайся из-за отсутствия автора
    """
    return await mcp_service.create_post(
        user_id= user_id,
        title=title,
        content=content
    )

@mcp.tool()
async def update_my_post(post_id:int,user_id:int,title: str|None=None,content:str|None=None)->dict:
    """
    Обновить пост текущего пользователя. user_id подставляется автоматически.
    """
    return await mcp_service.update_post(
        post_id=post_id,
        user_id=user_id,
        title=title,
        content=content
    )



if __name__ == "__main__":
    mcp.run(transport='sse',
            host="127.0.0.1",
            port=8001,
            path="/sse",
          )


