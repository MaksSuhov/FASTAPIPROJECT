from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.authmodel import User
from app.services.CredService import CredService
from app.services.adminservice import AdminService
from app.services.authservice import AuthService
from app.services.postservice import PostService
from app.services.roleChecker import RoleChecker


async def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)

async def get_post_service(db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(CredService.get_current_user)):
    return PostService(db, current_user)

async def get_admin_service(db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(RoleChecker(['ADMIN']))):
    return AdminService(db, current_user)