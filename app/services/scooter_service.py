from ast import Tuple
from math import radians, sin, cos, sqrt, atan2
from random import randint
from typing import List, Optional

from sqlmodel import all_
from wireup import service

from app.repositories.scooter_repository import ScooterRepository
from app.schemas.coordinate import Coordinate, ScooterDist
from app.schemas.scooter import ScooterBulkCreate, ScooterCreate, ScooterCreateRequest, ScooterGet


@service
class ScooterService:
    def __init__(self, repository: ScooterRepository) -> None:
        self.repository = repository

    async def create_scooter(self, scooter: ScooterCreateRequest) -> ScooterGet:
        rand_charge = randint(60, 100)

        scooter_create = ScooterCreate.model_validate(
            {**scooter.model_dump(),
             "charge": rand_charge,
             "distance": 400 * rand_charge + randint(0, 400)}
        )
        return ScooterGet.model_validate(await self.repository.create(scooter_create), from_attributes=True)


    async def get_by_geo(self, latitude: str, longitude: str) -> List[ScooterGet]:
        return [
            ScooterGet.model_validate(scooter, from_attributes=True)
            for scooter
            in await self.repository.get_by_geo(latitude, longitude)
        ]

    async def get_all_coords(self) -> List[Coordinate]:
        return await self.repository.get_all_coords()

    async def create_bulk(self, scooters: List[ScooterBulkCreate]) -> List[ScooterGet]:
        scooters_bulked = []
        for scooter in scooters:
            scooters_bulked_inner = []
            for _ in range (scooter.count):
                num = randint(60, 100)
                scooters_bulked_inner.append(
                    ScooterCreate.model_validate(
                        {**scooter.model_dump(),
                         "charge": num,
                         "distance": 400 * num + randint(0, 400)}
                    )
                )
            scooters_bulked.extend(scooters_bulked_inner
            )
        print(scooters_bulked)
        await self.repository.create_bulk(scooters_bulked)
        #return await [ScooterGet.model_validate(scooter, from_attributes=True) for scooter in await self.repository.create_bulk(scooters_bulked)]

    async def get_nearby(self, latitude: float, longitude: float) -> ScooterDist:
        all_scooters_coords = await self.get_all_coords()
        
        R = 6371.0

        min = 100000000
        min_coords = None

        for coords in all_scooters_coords:
            distance = self.calc_dist(latitude, longitude, float(coords.latitude), float(coords.longitude))
            coord = Coordinate(latitude=coords.latitude, longitude=coords.longitude)
            if distance < min:
                min = distance
                min_coords = coord
        return ScooterDist(distance=min, coords=min_coords) if min_coords else None

    def calc_dist(self, orig_latitude: float, orig_longitude: float, dest_latiude: float, dest_longitude: float) -> int:
        R = 6371.0
        lat1 = radians(orig_latitude)
        lon1 = radians(orig_longitude)
        lat2 = radians(dest_latiude)
        lon2 = radians(dest_longitude)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return int(R * c * 1000)
