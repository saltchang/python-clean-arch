from sqlalchemy import delete, or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.error import NotFoundError
from core.model.user import User
from core.protocol.repository.user import UserRepository
from core.type import IDType
from utility.decorator import singleton

from ..model import DbRole, DbUser


@singleton
class PsqlUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        role_ids = [role.id for role in user.roles]
        result = await self.session.execute(select(DbRole).where(DbRole.id.in_(role_ids)))
        db_roles = result.scalars().all()

        new_db_user = DbUser(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            is_verified=user.is_verified,
            roles=db_roles,
        )

        try:
            self.session.add(new_db_user)
            await self.session.commit()
            await self.session.refresh(new_db_user)
            return new_db_user.to_core()
        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def get_all(self) -> list[User]:
        result = await self.session.execute(select(DbUser))
        return [db_user.to_core() for db_user in result.scalars().all()]

    async def get_by_id(self, user_id: IDType) -> User | None:
        result = await self.session.execute(select(DbUser).where(DbUser.id == user_id))

        db_user = result.scalar_one_or_none()

        return db_user.to_core() if db_user else None

    async def get_by_username_or_email(self, username: str | None, email: str | None) -> User | None:
        result = await self.session.execute(
            select(DbUser).where(or_(DbUser.username == username, DbUser.email == email))
        )

        db_user = result.scalar_one_or_none()

        return db_user.to_core() if db_user else None

    async def update(self, user: User) -> User:
        existing_user = await self.session.execute(select(DbUser).where(DbUser.id == user.id))
        existing_user = existing_user.scalar_one_or_none()

        if not existing_user:
            raise NotFoundError('User not found')

        role_ids = [role.id for role in user.roles]
        result = await self.session.execute(select(DbRole).where(DbRole.id.in_(role_ids)))
        db_roles = result.scalars().all()

        await self.session.execute(
            update(DbUser)
            .where(DbUser.id == user.id)
            .values(
                username=user.username,
                email=user.email,
                password_hash=user.password_hash,
                is_verified=user.is_verified,
            )
        )

        existing_user.roles.clear()
        for role in db_roles:
            existing_user.roles.append(role)

        try:
            await self.session.commit()
            await self.session.refresh(existing_user)
            return existing_user.to_core()
        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def delete(self, user_id: IDType) -> None:
        await self.session.execute(delete(DbUser).where(DbUser.id == user_id))
        await self.session.commit()
