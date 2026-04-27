"""Logique metier pure du validateur de donnees capteur.

Cette couche ne depend pas de FastAPI : elle peut etre testee
unitairement sans serveur HTTP.
"""
from datetime import datetime, timezone
from typing import Dict

from src.config import get_thresholds
from src.schemas import ValidationResult


LEVEL_NORMAL = "normal"
LEVEL_MODERATE = "moderate"
LEVEL_CRITICAL = "critical"
LEVEL_UNKNOWN = "unknown"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def classify_value(value: float, moderate: float, critical: float) -> str:
    if value >= critical:
        return LEVEL_CRITICAL
    if value >= moderate:
        return LEVEL_MODERATE
    return LEVEL_NORMAL


def validate_sensor_data(sensor: str, value: float) -> Dict[str, object]:
    thresholds = get_thresholds(sensor)
    if thresholds is None:
        return ValidationResult(
            valid=False,
            level=LEVEL_UNKNOWN,
            message="Capteur non repertorie",
        ).model_dump(exclude_none=True)

    level = classify_value(value, thresholds["moderate"], thresholds["critical"])
    threshold_used = thresholds["critical"] if level == LEVEL_CRITICAL else thresholds["moderate"]
    is_valid = level != LEVEL_CRITICAL

    return ValidationResult(
        valid=is_valid,
        level=level,
        sensor=sensor.lower(),
        value=value,
        threshold=threshold_used,
        timestamp=utc_now_iso(),
    ).model_dump(exclude_none=True)
