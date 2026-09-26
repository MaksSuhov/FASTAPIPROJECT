from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rolemodel import Role
from app.repositories.authreposiory import AuthRepository


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_repository = AuthRepository

    async def get_by_name(self, name:str)-> Role | None:
        result = await self.db.execute(
            select(Role).where(Role.role_name == name)
        )
        return result.scalar_one_or_none()

    async def get_default_role(self)-> Role | None:
        return await self.get_by_name('USER')

    async def get_all(self)->list[Role]:
        list_role = await self.db.scalars(select(Role))
        return list_role.all()