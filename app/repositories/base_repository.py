from typing import Iterable, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel as BaseSchema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import Insert, Select, Update, Delete

from app.models.base import Base
from app.exceptions.infrastructure import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    EntityRelationDoesNotExistError
)
from app.core.database import Database


M = TypeVar("M", bound=Base)
C = TypeVar("C", bound=BaseSchema)
U = TypeVar("U", bound=BaseSchema)


class BaseRepository(Generic[M, C, U]):
    def __init__(self, model: M, database: Database) -> None:
        self.model = model
        self.produce_session = database.produce_session

    async def create(self, schema: C) -> M:
        async with self.produce_session() as session:
            stmt = (
                Insert(self.model)
                .values(schema.model_dump())
                .returning(self.model)
            )

            try:
                res = await session.execute(stmt)
                obj = res.scalars().unique().one()

                await session.commit()
                await session.refresh(obj)

                return obj
            except IntegrityError as e:
                err_msg = str(e.orig)

                if "foreign" in err_msg:
                    raise EntityRelationDoesNotExistError(
                        self.model.__name__
                    ) from e
                elif "unique" in err_msg:
                    raise EntityAlreadyExistsError(self.model.__name__) from e

    async def get(self, id: UUID) -> M:
        async with self.produce_session() as session:

            stmt = (
                Select(self.model)
                .where(self.model.id == id)
            )
            try:
                res = await session.execute(stmt)
                obj = res.scalars().unique().one()

                return obj
            except NoResultFound as e:
                raise EntityNotFoundError(self.model.__name__) from e

    async def update(self, id: UUID, schema: U) -> M:
        async with self.produce_session() as session:

            stmt = (
                Update(self.model)
                .where(self.model.id == id)
                .values(schema.model_dump())
                .returning(self.model)
            )

            try:
                res = await session.execute(stmt)
                obj = res.scalars().unique().one()

                await session.commit()
                await session.refresh(obj)

                return obj

            except NoResultFound as e:
                raise EntityNotFoundError(self.model.__name__) from e
            except IntegrityError as e:
                err_msg = str(e.orig)

                if "unique" in err_msg:
                    raise EntityAlreadyExistsError(
                        self.model.__name__
                    ) from e
                elif "foreign" in err_msg:
                    raise EntityRelationDoesNotExistError(
                        self.model.__name__
                    ) from e

    async def delete(self, id: UUID) -> None:
        async with self.produce_session() as session:

            stmt = Delete(self.model).where(self.model.id == id)

            try:
                res = await session.execute(stmt)
                await session.commit()

                if res.rowcount == 0:
                    raise NoResultFound

            except NoResultFound as e:
                raise EntityNotFoundError(self.model.__name__) from e

    async def get_all(self) -> Iterable[M]:
        async with self.produce_session() as session:

            stmt = Select(self.model)
            res = await session.execute(stmt)
            objs = res.scalars().unique().all()

            return objs

    async def list(
        self,
        limit: int,
        offset: int
    ) -> Iterable[M]:
        async with self.produce_session() as session:

            stmt = (
                Select(self.model)
                .offset(offset)
                .limit(limit)
            )
            res = await session.execute(stmt)
            objs = res.scalars().unique().all()

            return objs

    async def get_batch(
        self,
        ids: Iterable[UUID]
    ) -> Iterable[M]:
        async with self.produce_session() as session:

            stmt = (
                Select(self.model)
                .where(self.model.id.in_(ids))
            )
            try:
                res = await session.execute(stmt)
                objs = res.scalars().unique().all()

                return objs
            except NoResultFound as e:
                raise EntityNotFoundError(self.model.__name__) from e
