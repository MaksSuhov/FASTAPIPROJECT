import datetime

from sqlalchemy import ForeignKey, DateTime, Text, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.authmodel import User
from app.models.rolemodel import Role


class Conversation(Base):
    __tablename__ = 'conversations'

    conversation_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'),nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default= func.now() )
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    user: Mapped["User"] = relationship(back_populates="conversations")
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    message_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey ('conversations.conversation_id', ondelete='CASCADE'), nullable=False)
    content: Mapped[str] = mapped_column(Text,nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")