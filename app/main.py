from fastapi.params import Path

from app.models.authmodel import User
from app.models.rolemodel import Role
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import Base, engine, get_db
from app.api.routers.authrouter import router as authrouter
from app.api.routers.postrouter import router as postrouter
from app.api.routers.adminrouter import router as adminrouter
from app.api.routers.chatrouter import router as chatrouter


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(bind=engine) as db:
        try:
            admin_role = await db.scalar(
                select(Role).where(Role.role_name == 'ADMIN')
            )
            if not admin_role:
                db.add(Role(role_name='ADMIN', description="Администратор системы"))
                print("--- Роль ADMIN успешно создана ---")

            user_role = await db.scalar(
                select(Role).where(Role.role_name == 'USER')
            )
            if not user_role:
                db.add(Role(role_name='USER', description="Обычный пользователь"))
                print("--- Роль USER успешно создана ---")


            await db.commit()

        except Exception as e:
           await db.rollback()
           print(f"Ошибка при инициализации базовых ролей: {e}")

    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router=authrouter)
app.include_router(router=postrouter)
app.include_router(router=adminrouter)
app.include_router(router=chatrouter)

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # type: ignore
    allow_credentials=True,  # type: ignore
    allow_methods=["*"],  # type: ignore
    allow_headers=["*"]  # type: ignore
)

@app.post('/{user_id}/make-admin')
async def make_user_admin(user_id:int=Path(...,detail='айди юзера'),
                          db:AsyncSession=Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    admin_role = await db.scalar(
        select(Role).where(
            Role.role_name == 'ADMIN'
        ))
    if not admin_role:
        raise HTTPException(status_code=500, detail="Роль ADMIN не инициализирована в БД")

    if admin_role in user.roles:
        return {"message": "Пользователь уже админ"}

    user.roles.append(admin_role)
    await db.commit()

    return {'message': f'пользователь {user.user_name} теперь админ'}



