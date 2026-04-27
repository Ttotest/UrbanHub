"""Routes FastAPI du validateur de donnees capteur."""
from fastapi import APIRouter, status

from src.logic import validate_sensor_data
from src.schemas import SensorData, ValidationResult


router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health() -> dict:
    """Healthcheck utilise par docker-compose et le job deploy-staging du pipeline."""
    return {"status": "ok"}


@router.post(
    "/validate",
    response_model=ValidationResult,
    status_code=status.HTTP_200_OK,
)
def validate(payload: SensorData) -> dict:
    """Valide une donnee capteur et retourne sa classification metier.

    Ne renvoie jamais une erreur HTTP pour un capteur inconnu : la reponse
    est `level=unknown` avec `valid=False`, conformement au cas 4 du
    sujet EC03 (§3.3).
    """
    return validate_sensor_data(payload.sensor, payload.value)
