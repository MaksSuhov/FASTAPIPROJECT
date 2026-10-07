from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.chatmodel import Conversation, ChatMessage


class ChatRepository:
    def __init__(self, db: AsyncSession = Depends(get_db))->None:
        self.db = db

    async def create_new_conversation(self, user_id: int)->Conversation:
        conversation = Conversation(user_id=user_id)
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def get_owned_conversation(self, conversation_id: int, user_id: int)->Conversation | None:
        stmt = select(Conversation).where(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id
        )
        return await self.db.scalar(stmt)

    async def add_message(self, conversation_id: int, role:str, content: str) -> ChatMessage:
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.db.add(message)
        return message

    async def get_recent_message(self, conversation_id: int) -> list[ChatMessage]:
        stmt = select(ChatMessage).where(ChatMessage.conversation_id == conversation_id).order_by(
            ChatMessage.created_at.desc(),
            ChatMessage.message_id.desc()).limit(20)
        return list(reversed((await self.db.scalars(stmt)).all()))

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()
