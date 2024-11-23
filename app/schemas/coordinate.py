from pydantic import BaseModel


class Coordinate(BaseModel):
    latitude: str
    longitude: str


class ScooterDist(BaseModel):
    coordinate: Coordinate
    distance: int
