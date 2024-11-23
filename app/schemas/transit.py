from typing import List, Optional

from pydantic import BaseModel


class GeocodedWaypoint(BaseModel):
    geocoder_status: str
    place_id: str
    types: List[str]


class Northeast(BaseModel):
    lat: float
    lng: float


class Southwest(BaseModel):
    lat: float
    lng: float


class Bounds(BaseModel):
    northeast: Northeast
    southwest: Southwest


class ArrivalTime(BaseModel):
    text: str
    time_zone: str
    value: int


class DepartureTime(BaseModel):
    text: str
    time_zone: str
    value: int


class Distance(BaseModel):
    text: str
    value: int


class Duration(BaseModel):
    text: str
    value: int


class EndLocation(BaseModel):
    lat: float
    lng: float


class StartLocation(BaseModel):
    lat: float
    lng: float


class Distance1(BaseModel):
    text: str
    value: int


class Duration1(BaseModel):
    text: str
    value: int


class EndLocation1(BaseModel):
    lat: float
    lng: float


class Polyline(BaseModel):
    points: str


class StartLocation1(BaseModel):
    lat: float
    lng: float


class Distance2(BaseModel):
    text: str
    value: int


class Duration2(BaseModel):
    text: str
    value: int


class EndLocation2(BaseModel):
    lat: float
    lng: float


class Polyline1(BaseModel):
    points: str


class StartLocation2(BaseModel):
    lat: float
    lng: float


class Step1(BaseModel):
    distance: Distance2
    duration: Duration2
    end_location: EndLocation2
    html_instructions: Optional[str] = None
    polyline: Polyline1
    start_location: StartLocation2
    travel_mode: str
    maneuver: Optional[str] = None


class Location(BaseModel):
    lat: float
    lng: float


class ArrivalStop(BaseModel):
    location: Location
    name: str


class ArrivalTime1(BaseModel):
    text: str
    time_zone: str
    value: int


class Location1(BaseModel):
    lat: float
    lng: float


class DepartureStop(BaseModel):
    location: Location1
    name: str


class DepartureTime1(BaseModel):
    text: str
    time_zone: str
    value: int


class Agency(BaseModel):
    name: str
    phone: Optional[str] = None
    url: str


class Vehicle(BaseModel):
    icon: str
    name: str
    type: str


class Line(BaseModel):
    agencies: List[Agency]
    name: str
    short_name: Optional[str] = None
    vehicle: Vehicle
    color: Optional[str] = None
    text_color: Optional[str] = None


class TransitDetails(BaseModel):
    arrival_stop: ArrivalStop
    arrival_time: ArrivalTime1
    departure_stop: DepartureStop
    departure_time: DepartureTime1
    headsign: str
    line: Line
    num_stops: int


class Step(BaseModel):
    distance: Distance1
    duration: Duration1
    end_location: EndLocation1
    html_instructions: str
    polyline: Polyline
    start_location: StartLocation1
    steps: Optional[List[Step1]] = None
    travel_mode: str
    transit_details: Optional[TransitDetails] = None


class Leg(BaseModel):
    arrival_time: ArrivalTime
    departure_time: DepartureTime
    distance: Distance
    duration: Duration
    end_address: str
    end_location: EndLocation
    start_address: str
    start_location: StartLocation
    steps: List[Step]
    traffic_speed_entry: List
    via_waypoint: List


class OverviewPolyline(BaseModel):
    points: str


class Fare(BaseModel):
    currency: str
    text: str
    value: float


class Route(BaseModel):
    bounds: Bounds
    copyrights: str
    legs: List[Leg]
    overview_polyline: OverviewPolyline
    summary: str
    warnings: List[str]
    waypoint_order: List
    fare: Optional[Fare] = None


class TransitModel(BaseModel):
    geocoded_waypoints: List[GeocodedWaypoint]
    routes: List[Route]
    status: str
