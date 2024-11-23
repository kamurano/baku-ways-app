from app.models.base import Base


class Scooter(Base, table=True):
    latitude: str
    longitude: str

    charge: int
    distance: int
