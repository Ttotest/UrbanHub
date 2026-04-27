"""Logique metier pure du validateur de donnees capteur.

Cette couche ne depend pas de FastAPI : elle peut etre testee unitairement
sans serveur HTTP, ce qui est exige par le critere de Clean Code C19.2
(modularite + complexite cyclomatique faible).
"""
from datetime import datetime, timezone
from typing import Dict

from src.config import get_thresholds
from src.schemas import ValidationResult


LEVEL_NORMAL = "normal"
LEVEL_MODERATE = "moderate"
LEVEL_CRITICAL = "critical"
LEVEL_UNKNOWN = "unknown"

UNKNOWN_SENSOR_MESSAGE = "Capteur non repertorie"


def utc_now_iso() -> str:
    """Retourne l'horodatage UTC courant au format ISO-8601 (`...Z`).

    Format aligne sur l'exigence BC01 EX-INC-02 : tout incident horodate.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def classify_value(value: float, moderate: float, critical: float) -> str:
    """Classe une valeur capteur en `normal` / `moderate` / `critical`.

    Fonction pure : ne consulte aucun etat externe, ne fait aucun I/O.
    Complexite cyclomatique = 3, conforme aux limites SonarCloud.
    """
    if value >= critical:
        return LEVEL_CRITICAL
    if value >= moderate:
        return LEVEL_MODERATE
    return LEVEL_NORMAL


def _result_unknown() -> Dict[str, object]:
    return ValidationResult(
        valid=False,
        level=LEVEL_UNKNOWN,
        message=UNKNOWN_SENSOR_MESSAGE,
    ).model_dump(exclude_none=True)


def validate_sensor_data(sensor: str, value: float) -> Dict[str, object]:
    """Valide une donnee capteur et retourne le resultat structure.

    Comportement (cf sujet EC03 §3.3) :
      - capteur inconnu          -> level=unknown, valid=False, message
      - valeur < seuil modere    -> level=normal,   valid=True
      - valeur entre mod/crit    -> level=moderate, valid=True
      - valeur >= seuil critique -> level=critical, valid=False
    """
    thresholds = get_thresholds(sensor)
    if thresholds is None:
        return _result_unknown()

    level = classify_value(value, thresholds["moderate"], thresholds["critical"])
    threshold_used = (
        thresholds["critical"] if level == LEVEL_CRITICAL else thresholds["moderate"]
    )

    return ValidationResult(
        valid=level != LEVEL_CRITICAL,
        level=level,
        sensor=sensor.lower(),
        value=value,
        threshold=threshold_used,
        timestamp=utc_now_iso(),
    ).model_dump(exclude_none=True)
