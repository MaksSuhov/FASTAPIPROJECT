from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from starlette import status

from app.config.config import COOKIE_SECURE
from app.models.authmodel import User
from app.repositories.authreposiory import AuthRepository
from app.repositories.roleRepository import RoleRepository
from app.schemas.userschemas import Credentials
from app.services.CredService import CredService, ACCESS_TOKEN_EXPIRES_AT


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_repository = AuthRepository(db)
        self.role_repository = RoleRepository(db)


    async def register(self, cred:Credentials)->User:
        existed_user = await self.auth_repository.get_by_username(cred.user_name)
        if existed_user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

        default_role = await self.role_repository.get_default_role()

        new_user = User(
            user_name=cred.user_name,
            hash_password= await CredService.hash_password(cred.password),
            roles=[default_role]
        )

        await self.auth_repository.save(new_user)
        await self.db.commit()
        await self.db.refresh(
            new_user,
        attribute_names=['roles'])
        return new_user

    async def login(self, cred:Credentials, response: Response)->User:
        existed_user = await self.auth_repository.get_by_username(cred.user_name)
        if existed_user is None or not await CredService.verify_password(cred.password, existed_user.hash_password):
            raise HTTPException(status_code=404)

        access_token = CredService.create_access_token(existed_user.user_id)
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite='lax',
            max_age=ACCESS_TOKEN_EXPIRES_AT * 60,
            path='/'
        )
        return existed_user


