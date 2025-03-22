from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.future import select

from config.settings import APP_NAME, DATABASE_URL
from core.constant.user import DEFAULT_ROLE_DESCRIPTION, DEFAULT_ROLE_KEY, DEFAULT_ROLE_NAME

from .model.base import Base
from .model.user import DbRole


class Database:
    def __init__(self):
        self.engine: AsyncEngine = create_async_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True,
            connect_args={'server_settings': {'application_name': APP_NAME}},
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            autoflush=False,
        )

    async def create_all_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn))

        await self._create_default_roles()

    async def drop_all_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(sync_conn))

    async def _create_default_roles(self):
        async with self.async_session_maker() as session:
            result = await session.execute(select(DbRole).where(DbRole.key == DEFAULT_ROLE_KEY))
            existing_role = result.scalar_one_or_none()

            if existing_role:
                return

            new_role = DbRole(key=DEFAULT_ROLE_KEY, name=DEFAULT_ROLE_NAME, description=DEFAULT_ROLE_DESCRIPTION)
            session.add(new_role)
            await session.commit()


psql_db = Database()
