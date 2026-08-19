"""MS7 - Validateur d'occupation de stationnement (UrbanHub) - version initiale.

Point d'entree uvicorn : uvicorn src.validator:app --host 0.0.0.0 --port 8000
"""
import os
import json
from datetime import datetime
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Seuils d'occupation par type de zone (en %)
THRESHOLDS: Dict[str, Dict[str, int]] = {
    "surface": {"moderate": 70, "critical": 90},
    "souterrain": {"moderate": 75, "critical": 92},
    "silo": {"moderate": 80, "critical": 95},
    "pmr": {"moderate": 60, "critical": 80},
    "parc_relais": {"moderate": 85, "critical": 97},
}


class ParkingZoneData(BaseModel):
    zone_type: str = Field(..., description="Type de zone : surface, souterrain, silo, pmr, parc_relais")
    capacity: int = Field(..., ge=0)
    occupied: int = Field(..., ge=0)

app = FastAPI(title="UrbanHub - MS7 Validateur d'occupation de stationnement", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/validate")
def validate(payload: ParkingZoneData):
    """Valide et classifie une donnee d'occupation de zone."""
    print("payload recu : " + json.dumps(payload.dict()))
    thresholds = THRESHOLDS.get(payload.zone_type)
    if thresholds == None:
        return {"valid": False, "level": "unknown", "message": "Type de zone non répertorié"}
    if payload.capacity == 0:
        return {"valid": False, "level": "invalid", "message": "Données incohérentes : capacity doit être > 0"}
    if payload.occupied > payload.capacity:
        return {"valid": False, "level": "invalid", "message": "Données incohérentes : occupied > capacity"}
    try:
        rate = round(payload.occupied / payload.capacity * 100, 1)
    except:
        rate = 0.0
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    if rate >= thresholds["critical"]:
        return {"valid": False, "level": "critical", "zone_type": payload.zone_type, "occupied": payload.occupied, "capacity": payload.capacity, "rate": rate, "threshold": thresholds["critical"], "timestamp": timestamp}
    elif rate >= thresholds["moderate"]:
        return {"valid": True, "level": "moderate", "zone_type": payload.zone_type, "occupied": payload.occupied, "capacity": payload.capacity, "rate": rate, "threshold": thresholds["moderate"], "timestamp": timestamp}
    else:
        return {"valid": True, "level": "normal", "zone_type": payload.zone_type, "occupied": payload.occupied, "capacity": payload.capacity, "rate": rate, "threshold": thresholds["moderate"], "timestamp": timestamp}
