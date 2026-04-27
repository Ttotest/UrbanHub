"""Schemas Pydantic pour les entrees et sorties de l'API."""
from typing import Optional

from pydantic import BaseModel, Field


class SensorData(BaseModel):
    """Donnee capteur recue par l'endpoint POST /validate."""

    sensor: str = Field(
        min_length=1,
        max_length=64,
        description="Identifiant du capteur (ex: co2, temperature, pm25, humidity).",
    )
    value: float = Field(
        description="Valeur mesuree par le capteur, dans son unite native.",
    )


class ValidationResult(BaseModel):
    """Resultat structure retourne par l'endpoint POST /validate."""

    valid: bool
    level: str
    sensor: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: Optional[str] = None
    message: Optional[str] = None
