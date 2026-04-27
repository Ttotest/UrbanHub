"""Routes FastAPI du validateur de donnees capteur."""
from fastapi import APIRouter

from src.logic import validate_sensor_data
from src.schemas import SensorData


router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/validate")
def validate(payload: SensorData) -> dict:
    return validate_sensor_data(payload.sensor, payload.value)
