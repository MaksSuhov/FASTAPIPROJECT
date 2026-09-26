from datetime import datetime, timezone, timedelta

from fastapi import Cookie, Depends, HTTPException, status
from pwdlib import PasswordHash
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import SECRET_KEY
from app.database.database import get_db
from app.models.authmodel import User

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_AT = 60
password_hash = PasswordHash.recommended()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="необходимо авторизоваться"
)


class CredService:
    def __init__(self, db: AsyncSession)->None:
        self.db = db

    async def hash_password(password:str):
        return password_hash.hash(password)

    async def verify_password(password:str, hashed_password:str):
        return password_hash.verify(password, hashed_password)

    def create_access_token(user_id:int):
        expire_token = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRES_AT)
        access_token = {'sub':str(user_id), 'exp':expire_token}
        return jwt.encode(access_token,SECRET_KEY,algorithm=ALGORITHM)

    async def get_current_user(
            access_token: str | None = Cookie(default=None),
            db: AsyncSession = Depends(get_db)
    ):
        if access_token is None:
            raise credentials_exception
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = int(payload['sub'])
        except:
            raise credentials_exception

        user = await db.get(User, user_id)
        if user is None:
            raise credentials_exception
        return user
