"""Schemas Pydantic pour les entrees / sorties de l'API."""
from typing import Optional

from pydantic import BaseModel, Field


class SensorData(BaseModel):
    sensor: str = Field(min_length=1, max_length=64)
    value: float


class ValidationResult(BaseModel):
    valid: bool
    level: str
    sensor: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: Optional[str] = None
    message: Optional[str] = None
