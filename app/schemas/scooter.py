from random import randint
from uuid import UUID

from pydantic import BaseModel, Field


class ScooterCreateRequest(BaseModel):
    latitude: str
    longitude: str


class ScooterCreate(ScooterCreateRequest):
    charge: int
    distance: int


class ScooterUpdate(BaseModel):
    latitude: str
    longitude: str

    charge: int
    distance: int


class ScooterGet(ScooterCreate):
    id: UUID


class ScooterBulkCreate(ScooterCreateRequest):
    count: int
