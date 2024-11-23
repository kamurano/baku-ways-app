from typing import Annotated, List

from fastapi import APIRouter, Query, status
from wireup import Inject

from app.core.container import container
from app.schemas.coordinate import Coordinate
from app.schemas.scooter import ScooterBulkCreate, ScooterCreateRequest, ScooterGet
from app.services.scooter_service import ScooterService


router = APIRouter(prefix="/scooters", tags=["scooters"])


@router.get("/geo")
@container.autowire
async def get_distance(
    scooter_service: Annotated[ScooterService, Inject()],
) -> List[Coordinate]:
    return await scooter_service.get_all_coords()


@router.post("/", status_code=status.HTTP_201_CREATED)
@container.autowire
async def create_scooter(
    scooter: ScooterCreateRequest,
    scooter_service: Annotated[ScooterService, Inject()],
) -> ScooterGet:
    return await scooter_service.create_scooter(scooter)


@router.get("/")
@container.autowire
async def get_by_geo(
    latitude: Annotated[str, Query(..., description="Latitude")],
    longitude: Annotated[str, Query(..., description="Longitude")],
    scooter_service: Annotated[ScooterService, Inject()],
) -> List[ScooterGet]:
    return await scooter_service.get_by_geo(latitude, longitude)


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
@container.autowire
async def create_bulk(
    scooters: List[ScooterBulkCreate],
    scooter_service: Annotated[ScooterService, Inject()],
):
    await scooter_service.create_bulk(scooters)
    return {"message": "Scooters created successfully"}