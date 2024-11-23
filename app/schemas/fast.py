from typing import List

from pydantic import BaseModel, ConfigDict

from app.enums.transport_type import TransportType


class Path(BaseModel):
    distance: str
    duration: str
    start_latitude: str
    start_longitude: str
    end_latitude: str
    end_longitude: str
    polyline: str
    type: TransportType

    model_config = ConfigDict(use_enum_values=True)


class FastResponse(BaseModel):
    paths: List[Path] = []


