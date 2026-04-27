"""Tests pytest pour le microservice ms6-validateur-capteur.

Couvre :
  - test_normal           : valeur < seuil modere      -> normal,    valid=True
  - test_moderate         : valeur entre modere/crit   -> moderate,  valid=True
  - test_critical         : valeur >= seuil critique   -> critical,  valid=False
  - test_unknown_sensor   : capteur non repertorie     -> unknown,   valid=False
  - test_capteur_ajoute   : 5e capteur (humidity)      -> classification correcte
  - test_health           : endpoint /health
  - test_classify_value   : couverture de la logique pure
"""
from fastapi.testclient import TestClient

from src.logic import (
    LEVEL_CRITICAL,
    LEVEL_MODERATE,
    LEVEL_NORMAL,
    classify_value,
    validate_sensor_data,
)
from src.validator import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_normal() -> None:
    response = client.post("/validate", json={"sensor": "co2", "value": 500.0})

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["level"] == LEVEL_NORMAL
    assert body["sensor"] == "co2"
    assert body["value"] == 500.0
    assert body["threshold"] == 800
    assert "timestamp" in body


def test_moderate() -> None:
    response = client.post("/validate", json={"sensor": "co2", "value": 850.0})

    body = response.json()
    assert response.status_code == 200
    assert body["valid"] is True
    assert body["level"] == LEVEL_MODERATE
    assert body["threshold"] == 800


def test_critical() -> None:
    response = client.post("/validate", json={"sensor": "co2", "value": 1500.0})

    body = response.json()
    assert response.status_code == 200
    assert body["valid"] is False
    assert body["level"] == LEVEL_CRITICAL
    assert body["threshold"] == 1000


def test_unknown_sensor() -> None:
    response = client.post("/validate", json={"sensor": "radioactivity", "value": 1.0})

    body = response.json()
    assert response.status_code == 200
    assert body["valid"] is False
    assert body["level"] == "unknown"
    assert body["message"] == "Capteur non repertorie"


def test_capteur_ajoute_humidity_normal() -> None:
    response = client.post("/validate", json={"sensor": "humidity", "value": 40.0})

    body = response.json()
    assert response.status_code == 200
    assert body["valid"] is True
    assert body["level"] == LEVEL_NORMAL
    assert body["sensor"] == "humidity"


def test_capteur_ajoute_humidity_critical() -> None:
    response = client.post("/validate", json={"sensor": "humidity", "value": 95.0})

    body = response.json()
    assert response.status_code == 200
    assert body["valid"] is False
    assert body["level"] == LEVEL_CRITICAL


def test_temperature_moderate() -> None:
    response = client.post("/validate", json={"sensor": "temperature", "value": 36.5})

    body = response.json()
    assert response.status_code == 200
    assert body["level"] == LEVEL_MODERATE
    assert body["valid"] is True


def test_classify_value_pure_logic() -> None:
    assert classify_value(10.0, 20.0, 50.0) == LEVEL_NORMAL
    assert classify_value(20.0, 20.0, 50.0) == LEVEL_MODERATE
    assert classify_value(49.9, 20.0, 50.0) == LEVEL_MODERATE
    assert classify_value(50.0, 20.0, 50.0) == LEVEL_CRITICAL
    assert classify_value(999.0, 20.0, 50.0) == LEVEL_CRITICAL


def test_validate_sensor_data_pure_unknown() -> None:
    result = validate_sensor_data("ghost-sensor", 42.0)

    assert result["valid"] is False
    assert result["level"] == "unknown"
    assert "message" in result


def test_validate_uppercase_sensor_is_normalized() -> None:
    response = client.post("/validate", json={"sensor": "CO2", "value": 850.0})

    body = response.json()
    assert response.status_code == 200
    assert body["sensor"] == "co2"
    assert body["level"] == LEVEL_MODERATE


def test_validate_rejects_missing_value() -> None:
    response = client.post("/validate", json={"sensor": "co2"})

    assert response.status_code == 422
