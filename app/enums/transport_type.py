from enum import StrEnum, auto


class TransportType(StrEnum):
    DRIVE = auto()
    BUS = auto()
    SUBWAY = auto()
    WALKING = auto()
    BICYCLE = auto()
