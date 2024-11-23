from typing import Annotated, List

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from wireup import Inject

from app.core.container import container
from app.schemas.fast import FastResponse
from app.services.scooter_service import ScooterService
from configs.settings import Settings


router = APIRouter(prefix="/fast", tags=["Fast"])


class Polyline(BaseModel):
    encodedPolyline: str


class Route(BaseModel):
    distanceMeters: int
    duration: str
    polyline: Polyline


class DriveModel(BaseModel):
    routes: List[Route]


async def get_distance_and_polyline_drive(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
    settings: Settings,
) -> Route:
    async with httpx.AsyncClient() as client:
        url = settings.GOOGLE_MAPS_DRIVE_API_URL
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
        }
        data = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": origin_lat,
                        "longitude": origin_lon
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": destination_lat,
                        "longitude": destination_lon
                    }
                }
            },
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "computeAlternativeRoutes": False,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            },
            "languageCode": "en-US",
            "units": "IMPERIAL"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code == 200:
                try:
                    obj = DriveModel.model_validate(response.json(), from_attributes=True)
                    return obj.routes[0] 
                except Exception as e:
                    raise HTTPException(status_code=400, detail="Error fetching route data")
            else:
                raise HTTPException(status_code=400, detail="Error fetching route data")


async def get_distance_and_polyline_bicycle(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
    settings: Settings,
) -> Route:
    data = await get_distance_and_polyline_drive(
        origin_lat, origin_lon, destination_lat, destination_lon, settings
    )
    data.duration = f"{int(data.distanceMeters * 3600 / 23500)}s"
    return data




@router.get("/")
@container.autowire
async def get_fast_map(
    origin_lat: Annotated[float, Query(description="Origin Latitude")],
    origin_lon: Annotated[float, Query(description="Origin Longitude")],
    destination_lat: Annotated[float, Query(description="Destination Latitude")],
    destination_lon: Annotated[float, Query(description="Destination Longitude")],
    scooter_service: Annotated[ScooterService, Inject()],
    settings: Annotated[Settings, Inject()],
) -> FastResponse:
    response = FastResponse()
    
    orig_scooter = await scooter_service.get_nearby(origin_lat, origin_lon)
    dest_scooter = await scooter_service.get_nearby(destination_lat, destination_lon)
    between_stations = scooter_service.calc_dist(
        orig_latitude=orig_scooter.coordinate.latitude,
        orig_longitude=orig_scooter.coordinate.longitude,
        dest_latiude=dest_scooter.coordinate.latitude,
        dest_longitude=dest_scooter.coordinate.longitude,
    )

    if orig_scooter.distance <= 500 and dest_scooter.distance <= 500 and between_stations < 20000:
        response.paths.append(await get_distance_and_polyline_bicycle(
            orig_scooter.coordinate.latitude,
            orig_scooter.coordinate.longitude,
            dest_scooter.coordinate.latitude,
            dest_scooter.coordinate.longitude,
            settings
        )) + ...
   