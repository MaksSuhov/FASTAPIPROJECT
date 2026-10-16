from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.postmodel import Post



class Like(Base):
    __tablename__ = "likes"

    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.post_id', ondelete='CASCADE'), primary_key=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False )
  