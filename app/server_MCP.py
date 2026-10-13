from datetime import datetime
import logging
from typing import Any
from fastmcp.dependencies import Depends
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token


from app.config.config import SECRET_KEY
from app.database.database import AsyncSessionLocal
from app.mcp_token import MCP_ALGORITHM, MCP_AUDIENCE
from app.repositories.postrepository import PostRepository
from app.schemas.postschemas import PostCreateSchema
from app.services.mcpservice import McpServise
from app.services.postservice import PostService


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    'PRACTICESERVER',
    auth=JWTVerifier(
        public_key=SECRET_KEY,
        algorithm=MCP_ALGORITHM,
        audience=MCP_AUDIENCE,
    ),
)

mcp_service = McpServise(AsyncSessionLocal)

def current_user_id()->int:
    token = get_access_token()
    if token is None:
        raise RuntimeError("нет токена: тул вызывается только через SSE с заголовком Authorization")
    return int(token.subject)

@mcp.tool
async def get_my_profile(user_id:int = Depends(current_user_id))->dict:
    """
    получить информацию о пользователе, user_id подставляется автоматически.
    """
    return await mcp_service.get_profile(user_id)
    

@mcp.tool()
async def get_user_posts(user_id: int = Depends(current_user_id)) -> dict:
    """
    Асинхронно получить список постов текущего пользователя из внутренней базы данных.
    """
    return await mcp_service.get_posts(user_id=user_id)

@mcp.tool()
async def mcp_create_post(title:str, content:str, user_id:int = Depends(current_user_id))->dict:
    """
    Создать пост от имени текущего пользователя. Как с задными title, content так и с наполнением от ассистента.
    """
    return await mcp_service.create_post(
        user_id= user_id,
        title=title,
        content=content
    )

@mcp.tool()
async def update_my_post(post_id:int,title: str|None=None,content:str|None=None, user_id:int = Depends(current_user_id))->dict:
    """
    Обновить пост текущего пользователя.
    """
    return await mcp_service.update_post(
        post_id=post_id,
        user_id=user_id,
        title=title,
        content=content
    )

@mcp.tool()
async def delete_my_post(post_id:int, user_id:int = Depends(current_user_id))->dict:
    """
    удалить пост текущего пользователя.
    """
    return await mcp_service.delete_post(
        user_id=user_id,
        post_id=post_id
    )


if __name__ == "__main__":
    mcp.run(transport='sse',
            host="127.0.0.1",
            port=8001,
            path="/sse",
          )


