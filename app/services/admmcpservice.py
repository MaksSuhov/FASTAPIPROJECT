from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from app.database.database import AsyncSessionLocal
from app.models.authmodel import User
from app.repositories.authreposiory import AuthRepository







class AdminMCPService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession])->None:
        self.session_factory = session_factory

    async def get_all_users(self)->dict:
        async with self.session_factory() as db_session:
            users = await AuthRepository(db_session).get_all_users()

            if users is None:
                return {'error': "Не удалось получить пользователей"}

            formatted_users = [{
                'user_name': user.user_name,
                'user_id': user.user_id,
                'roles': [r.role_name for r in user.roles],
                'created_at': user.created_at.isoformat()
                } for user in users
            ]
            return {
                'users_count': len(formatted_users),
                'users': formatted_users
            }