"""MS7 - Validateur d'occupation de stationnement (UrbanHub).

Porte de qualite du domaine stationnement : avant qu'une donnee
d'occupation soit propagee sur le bus d'evenements, elle est validee
puis classifiee (normal / moderate / critical) selon des seuils par
type de zone.

Point d'entree uvicorn :

    uvicorn src.validator:app --host 0.0.0.0 --port 8000

Le module est decoupe en quatre parties independantes (C19) :
  1. configuration des seuils      -> THRESHOLDS
  2. schema d'entree               -> ParkingZoneData
  3. logique metier pure           -> compute_rate / classify / validate_zone
  4. exposition HTTP (FastAPI)     -> app, POST /validate
"""
from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# 1. Configuration des seuils (en % d'occupation)
# ---------------------------------------------------------------------------
THRESHOLDS: Dict[str, Dict[str, int]] = {
    "surface": {"moderate": 70, "critical": 90},
    "souterrain": {"moderate": 75, "critical": 92},
    "silo": {"moderate": 80, "critical": 95},
    "pmr": {"moderate": 60, "critical": 80},
    # Type de zone supplementaire (choix libre) : parc relais (P+R) en
    # peripherie. Grande capacite, se remplit tot le matin : on tolere un
    # taux plus haut avant d'alerter.
    "parc_relais": {"moderate": 85, "critical": 97},
}

LEVEL_NORMAL = "normal"
LEVEL_MODERATE = "moderate"
LEVEL_CRITICAL = "critical"
LEVEL_UNKNOWN = "unknown"
LEVEL_INVALID = "invalid"

MSG_UNKNOWN_ZONE = "Type de zone non répertorié"
MSG_INCONSISTENT = "Données incohérentes : occupied > capacity"
MSG_ZERO_CAPACITY = "Données incohérentes : capacity doit être > 0"


# ---------------------------------------------------------------------------
# 2. Schema d'entree
# ---------------------------------------------------------------------------
class ParkingZoneData(BaseModel):
    """Donnee d'occupation d'une zone de stationnement recue du collecteur."""

    zone_type: str = Field(..., description="surface, souterrain, silo, pmr...")
    capacity: int = Field(..., ge=0, description="Nombre total de places")
    occupied: int = Field(..., ge=0, description="Nombre de places occupees")


# ---------------------------------------------------------------------------
# 3. Logique metier
# ---------------------------------------------------------------------------
def utc_timestamp() -> str:
    """Horodatage UTC au format ISO 8601 court (ex: 2026-08-19T09:00:00Z)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def compute_rate(occupied: int, capacity: int) -> float:
    """Taux d'occupation en %, arrondi a une decimale."""
    return round(occupied / capacity * 100, 1)


def classify(rate: float, thresholds: Dict[str, int]) -> str:
    """Classe un taux d'occupation par rapport aux seuils d'une zone."""
    if rate >= thresholds["critical"]:
        return LEVEL_CRITICAL
    if rate >= thresholds["moderate"]:
        return LEVEL_MODERATE
    return LEVEL_NORMAL


def _rejection(level: str, message: str) -> Dict[str, object]:
    """Reponse commune aux cas rejetes (zone inconnue, donnees incoherentes)."""
    return {"valid": False, "level": level, "message": message}


def _check_consistency(data: ParkingZoneData) -> Optional[str]:
    """Retourne un message d'erreur si la donnee est incoherente, sinon None."""
    if data.capacity == 0:
        return MSG_ZERO_CAPACITY
    if data.occupied > data.capacity:
        return MSG_INCONSISTENT
    return None


def validate_zone(data: ParkingZoneData) -> Dict[str, object]:
    """Valide et classifie une donnee d'occupation (cas 1 a 5 du sujet)."""
    thresholds = THRESHOLDS.get(data.zone_type)
    if thresholds is None:
        return _rejection(LEVEL_UNKNOWN, MSG_UNKNOWN_ZONE)

    error = _check_consistency(data)
    if error is not None:
        return _rejection(LEVEL_INVALID, error)

    rate = compute_rate(data.occupied, data.capacity)
    level = classify(rate, thresholds)
    threshold_key = "critical" if level == LEVEL_CRITICAL else "moderate"
    return {
        "valid": level != LEVEL_CRITICAL,
        "level": level,
        "zone_type": data.zone_type,
        "occupied": data.occupied,
        "capacity": data.capacity,
        "rate": rate,
        "threshold": thresholds[threshold_key],
        "timestamp": utc_timestamp(),
    }


# ---------------------------------------------------------------------------
# 4. Exposition HTTP
# ---------------------------------------------------------------------------
app = FastAPI(
    title="UrbanHub - MS7 Validateur d'occupation de stationnement",
    version="1.0.0",
    description=(
        "Valide une donnee d'occupation de zone de stationnement et la "
        "classifie (normal / moderate / critical) selon les seuils par type "
        "de zone."
    ),
)


@app.get("/health")
def health() -> Dict[str, str]:
    """Healthcheck utilise par docker-compose et le job deploy-staging."""
    return {"status": "ok"}


@app.post("/validate")
def validate(payload: ParkingZoneData) -> Dict[str, object]:
    """Valide une donnee d'occupation et retourne sa classification.

    Ne renvoie jamais d'erreur HTTP pour un cas metier (zone inconnue,
    donnees incoherentes) : la reponse porte `valid=False` et un `message`,
    conformement aux cas 4 et 5 du sujet.
    """
    return validate_zone(payload)
