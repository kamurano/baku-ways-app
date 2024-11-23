from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.scooter import router as scooter_router
from app.routers.taxi_optima import router as taxi_optima_router
from app.routers.transit import router as transit_router


app = FastAPI(
    title="Scooter API",
    version="0.0.1",
    description="API for Scooter",
)

app.include_router(scooter_router)
app.include_router(taxi_optima_router)
app.include_router(transit_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
