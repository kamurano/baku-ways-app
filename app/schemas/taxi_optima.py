from pydantic import BaseModel, Field
from typing import List, Tuple, Dict


class TaxiOptimaRequest(BaseModel):
    user_latitude: str
    user_longitude: str
    destination_latitude: str
    destination_longitude: str
    
    
class TaxiOptimaResponse(BaseModel):
    optimal_start_latitude: str
    optimal_start_longitude: str
    destination_latitude: str
    destination_longitude: str
    trip_distance: float
    trip_duration: float
    user_to_pickup_distance: float
    user_to_pickup_polyline: str
    taxi_to_pickup_distance: float
    pickup_to_dest_distance: float
    coordinates: List[Tuple[float, float]]
    instructions: List[Dict]
    pickup_to_dest_polyline: str
    taxi_to_pickup_polyline: str
    taxi_coming_coordinates: List[Tuple[float, float]]
    taxi_wait_time: float
    taxi_wait_distance: float
    