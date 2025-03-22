from sqlalchemy import Boolean, Column, ForeignKey, Integer, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.model.user import Role, User
from core.type import IDType

from .base import Base, TimestampedMixin


class DbRole(Base, TimestampedMixin):
    __tablename__ = 'role'

    id: Mapped[IDType] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    key: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    users: Mapped[list['DbUser']] = relationship(
        'DbUser',
        secondary='user_roles',
        back_populates='roles',
        lazy='selectin',
    )

    def to_core(self) -> Role:
        return Role(
            id=self.id,
            name=self.name,
            key=self.key,
        )


class DbUser(Base, TimestampedMixin):
    __tablename__ = 'end_user'

    id: Mapped[IDType] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=True)  # nullable for third-party auth
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    roles: Mapped[list['DbRole']] = relationship(
        'DbRole',
        secondary='user_roles',
        back_populates='users',
        lazy='selectin',
    )

    def to_core(self) -> User:
        return User(
            id=self.id,
            username=self.username,
            email=self.email,
            password_hash=self.password_hash,
            is_verified=self.is_verified,
            roles=[role.to_core() for role in self.roles],
        )


user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('end_user.id', ondelete='CASCADE')),
    Column('role_id', Integer, ForeignKey('role.id', ondelete='CASCADE')),
    UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
)
