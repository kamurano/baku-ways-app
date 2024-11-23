import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_scoped_session,
    async_sessionmaker,
)

from app.exceptions.infrastructure import DatabaseUnreachableError
from configs.settings import Settings


class Database:
    def __init__(self, settings: Settings) -> None:
        self._engine = create_async_engine(
            url=settings.POSTGRES_URI,
            echo=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800,
            # pool_pre_ping=True
        )
        self._session_factory = async_scoped_session(
            async_sessionmaker(
                autocommit=False,
                expire_on_commit=False,
                autoflush=False,
                bind=self._engine,
            ),
            scopefunc=asyncio.current_task,
        )

    @asynccontextmanager
    async def produce_session(self) -> AsyncGenerator[
        AsyncSession,
        None
    ]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except DBAPIError as e:
            # logger.error(f"Database Error: {e}")
            await session.rollback()
            raise DatabaseUnreachableError(e)
        finally:
            await session.close()
