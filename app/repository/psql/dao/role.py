from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.model.user import Role
from core.protocol.repository.role import RoleRepository
from core.type import IDType
from utility.decorator import singleton

from ..model import DbRole


@singleton
class PsqlRoleRepository(RoleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_key(self, key: str) -> Role | None:
        result = await self.session.execute(select(DbRole).where(DbRole.key == key))
        db_role = result.scalar_one_or_none()

        return db_role.to_core() if db_role else None

    async def get_by_ids(self, ids: list[IDType]) -> list[Role]:
        if not ids:
            return []

        result = await self.session.execute(select(DbRole).where(DbRole.id.in_(ids)))
        return [db_role.to_core() for db_role in result.scalars().all()]
