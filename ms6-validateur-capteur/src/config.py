"""Configuration des seuils metiers pour le validateur de donnees capteur.

Les seuils proviennent du sujet EC03 (BC01 EX-ENV-02). On y ajoute un capteur
supplementaire (humidity) conformement a la consigne "ajouter au moins un
capteur supplementaire".
"""
from typing import Dict, TypedDict


class Thresholds(TypedDict):
    moderate: float
    critical: float
    unit: str


THRESHOLDS: Dict[str, Thresholds] = {
    "co2":         {"moderate": 800.0,  "critical": 1000.0, "unit": "ppm"},
    "temperature": {"moderate": 35.0,   "critical": 40.0,   "unit": "C"},
    "noise":       {"moderate": 70.0,   "critical": 85.0,   "unit": "dB"},
    "pm25":        {"moderate": 25.0,   "critical": 50.0,   "unit": "ug/m3"},
    "humidity":    {"moderate": 70.0,   "critical": 85.0,   "unit": "percent"},
}


def get_thresholds(sensor: str) -> Thresholds | None:
    return THRESHOLDS.get(sensor.lower())
