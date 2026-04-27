"""Configuration des seuils metiers pour le validateur de donnees capteur.

Les seuils proviennent du sujet EC03 (BC01 EX-ENV-02). On y ajoute deux
capteurs supplementaires (humidity, illuminance) conformement a la consigne
"ajouter au moins un capteur supplementaire". Les chiffres sont alignes sur
les ordres de grandeur usuels en environnement urbain.

Le dictionnaire `THRESHOLDS` est volontairement le seul point de configuration
metier ; toute la logique de classification vit dans `src.logic`.
"""
from typing import Dict, Optional, TypedDict


class Thresholds(TypedDict):
    """Couple seuil modere / critique pour un capteur, plus son unite."""

    moderate: float
    critical: float
    unit: str


THRESHOLDS: Dict[str, Thresholds] = {
    "co2":         {"moderate": 800.0,  "critical": 1000.0, "unit": "ppm"},
    "temperature": {"moderate": 35.0,   "critical": 40.0,   "unit": "C"},
    "noise":       {"moderate": 70.0,   "critical": 85.0,   "unit": "dB"},
    "pm25":        {"moderate": 25.0,   "critical": 50.0,   "unit": "ug/m3"},
    "humidity":    {"moderate": 70.0,   "critical": 85.0,   "unit": "percent"},
    "illuminance": {"moderate": 1500.0, "critical": 5000.0, "unit": "lux"},
}


def get_thresholds(sensor: str) -> Optional[Thresholds]:
    """Retourne les seuils du capteur ou None si non repertorie.

    La cle est normalisee en minuscules pour accepter les variantes (`CO2`,
    `Co2`, `co2`).
    """
    if not sensor:
        return None
    return THRESHOLDS.get(sensor.lower())
