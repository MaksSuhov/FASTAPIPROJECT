import logging
from typing import Any
from fastmcp import FastMCP

from app.database.database import AsyncSessionLocal
from app.repositories.postrepository import PostRepository


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

mcp = FastMCP('PRACTICESERVER')


@mcp.tool
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
            posts = await repo.get_by_user_id(user_id)

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



if __name__ == "__main__":
    mcp.run(transport='sse',
            host="127.0.0.1",
            port=8001,
            path="/sse",
          )


