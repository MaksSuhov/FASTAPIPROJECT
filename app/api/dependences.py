from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.authmodel import User
from app.repositories.chatrepository import ChatRepository
from app.services.CredService import CredService
from app.services.OpenAIChatGateway import OpenAIChatGateway
from app.services.PromptBuilder import PromptBuilder
from app.services.adminservice import AdminService
from app.services.authservice import AuthService
from app.services.postservice import PostService
from app.services.roleChecker import RoleChecker
from app.services.chatservice import ChatService


async def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)

async def get_post_service(db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(CredService.get_current_user)):
    return PostService(db, current_user)

async def get_admin_service(db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(RoleChecker(['ADMIN']))):
    return AdminService(db, current_user)

async def get_chat_service(prompt_builder: PromptBuilder = Depends(PromptBuilder),
                           llm: OpenAIChatGateway = Depends(OpenAIChatGateway),
                           db: AsyncSession = Depends(get_db)
                           ):
    return ChatService(chat_repository=ChatRepository(db),
                       llm=llm,
                       prompt_builder=prompt_builder)



