from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models.authmodel import User
from app.services.CredService import CredService


class RoleChecker:
    def __init__(self, allowed_roles: list[str])->None:
        self.allowed_roles = allowed_roles

    def __call__(self,
                 current_user: User = Depends(CredService.get_current_user
                 ))->User:
        has_allowed_role = any(
            role.role_name in self.allowed_roles
            for role in current_user.roles
        )

        if not has_allowed_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )

        return current_user
