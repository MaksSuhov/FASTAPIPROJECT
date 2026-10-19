from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base



class Comment(Base):
    __tablename__ = 'comments'

    comment_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.post_id', ondelete='CASCADE'), nullable=False, index=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey('comments.comment_id', ondelete='CASCADE'), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
