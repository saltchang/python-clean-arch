from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from repository.psql.connection import psql_db
from repository.psql.dao.role import PsqlRoleRepository
from repository.psql.dao.user import PsqlUserRepository
from service.user import UserService


async def get_user_service() -> AsyncGenerator[UserService]:
    async with psql_db.async_session_maker() as session:
        try:
            yield UserService(
                user_repository=PsqlUserRepository(session),
                role_repository=PsqlRoleRepository(session),
            )
        finally:
            await session.close()


UserServiceDependency = Annotated[UserService, Depends(get_user_service)]
