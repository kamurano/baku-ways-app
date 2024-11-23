from typing import List

from sqlalchemy import Select
from sqlmodel import and_
from wireup import service

from app.core.database import Database
from app.models.base import Base
from app.models.scooter import Scooter
from app.repositories.base_repository import BaseRepository
from app.schemas.coordinate import Coordinate
from app.schemas.scooter import ScooterCreate, ScooterCreateRequest, ScooterUpdate


@service
class ScooterRepository(BaseRepository[Scooter, ScooterCreate, ScooterUpdate]):
    def __init__(self, database: Database):
        super().__init__(Scooter, database)

    async def get_by_geo(self, latitude: str, longitude: str) -> List[Scooter]:
        async with self.produce_session() as session:
            stmt = (
                Select(self.model)
                .where(
                    and_(
                        self.model.latitude == latitude,
                        self.model.longitude == longitude
                    )
                )
            )

            res = await session.execute(stmt)
            objs = res.scalars().all()

            return objs

    async def get_all_coords(self) -> List[Coordinate]:
        async with self.produce_session() as session:
            stmt = Select(
                self.model.latitude,
                self.model.longitude
            ).group_by(
                self.model.latitude,
                self.model.longitude
            )

            res = await session.execute(stmt)
            data = res.all()

            print(data)

            return [Coordinate.model_validate({"latitude": obj[0], "longitude": obj[1]}, from_attributes=True) for obj in data]

    async def create_bulk(self, scooters: List[ScooterCreate]) -> List[Scooter]:
        async with self.produce_session() as session:
            session.add_all([self.model.model_validate(scooter, from_attributes=True) for scooter in scooters])
            await session.commit()

            return scooters
