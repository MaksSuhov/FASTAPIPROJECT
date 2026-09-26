from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.authmodel import User


class AuthRepository:

    def __init__(self, db: AsyncSession)->None:
        self.db = db

    async def get_by_username(self, user_name: str)->User | None:
        return await self.db.scalar(
            select(User).where(User.user_name == user_name).options(selectinload(User.roles)))

    async def get_by_id(self, user_id:int)->User:
         return await self.db.get(User, user_id)

    async def save(self, new_user: User)->User:
        self.db.add(new_user)
        return new_user

