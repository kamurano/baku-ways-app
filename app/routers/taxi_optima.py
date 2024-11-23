from typing import Annotated, List

from fastapi import APIRouter, Query, status
from wireup import Inject

from app.core.container import container
from app.schemas.coordinate import Coordinate
from app.schemas.taxi_optima import TaxiOptimaRequest, TaxiOptimaResponse
from app.services.taxi_optima import TaxiOptimaService


router = APIRouter(prefix="/taxi-optima", tags=["taxi-optima"])


@router.post("/request", status_code=status.HTTP_200_OK)
@container.autowire
async def create_taxi_optima(
    taxi_optima: TaxiOptimaRequest,
    taxi_optima_service: Annotated[TaxiOptimaService, Inject()],
) -> TaxiOptimaResponse:
    return taxi_optima_service.request_taxi_optima(taxi_optima)