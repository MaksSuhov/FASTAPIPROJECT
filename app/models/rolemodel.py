from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.authmodel import User

class Role(Base):
    __tablename__ = 'roles'

    role_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_name: Mapped[str] = mapped_column(String(49),unique=True)
    description: Mapped[str] = mapped_column(String(255))

    users: Mapped[list['User']] = relationship(
        secondary='user_roles',
        back_populates='roles'
    )

class UserRole(Base):
    __tablename__ = 'user_roles'

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id",ondelete='CASCADE'),primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete='CASCADE'),primary_key=True)