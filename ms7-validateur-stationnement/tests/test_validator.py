"""Tests pytest du validateur d'occupation de stationnement (MS7).

Les 5 tests obligatoires du sujet (test_normal, test_moderate,
test_critical, test_unknown_zone, test_invalid_data) passent par
l'endpoint HTTP POST /validate. Les tests complementaires couvrent
la logique pure (compute_rate, classify) et les cas limites.
"""
import re

from fastapi.testclient import TestClient

from src.validator import (
    THRESHOLDS,
    ParkingZoneData,
    app,
    classify,
    compute_rate,
    validate_zone,
)

client = TestClient(app)


def post_validate(zone_type: str, capacity: int, occupied: int) -> dict:
    response = client.post(
        "/validate",
        json={"zone_type": zone_type, "capacity": capacity, "occupied": occupied},
    )
    assert response.status_code == 200
    return response.json()


# ---------------------------------------------------------------------------
# 5 tests obligatoires (sujet C17)
# ---------------------------------------------------------------------------
def test_normal():
    body = post_validate("surface", 50, 20)
    assert body["valid"] is True
    assert body["level"] == "normal"
    assert body["rate"] == 40.0
    assert body["threshold"] == 70


def test_moderate():
    body = post_validate("surface", 50, 38)
    assert body["valid"] is True
    assert body["level"] == "moderate"
    assert body["rate"] == 76.0
    assert body["threshold"] == 70


def test_critical():
    body = post_validate("surface", 50, 46)
    assert body["valid"] is False
    assert body["level"] == "critical"
    assert body["rate"] == 92.0
    assert body["threshold"] == 90


def test_unknown_zone():
    body = post_validate("aeroport", 50, 20)
    assert body["valid"] is False
    assert body["level"] == "unknown"
    assert body["message"] == "Type de zone non répertorié"


def test_invalid_data():
    body = post_validate("surface", 50, 60)
    assert body["valid"] is False
    assert body["level"] == "invalid"
    assert "occupied > capacity" in body["message"]


# ---------------------------------------------------------------------------
# Tests complementaires
# ---------------------------------------------------------------------------
def test_response_contract_and_timestamp_utc():
    body = post_validate("souterrain", 100, 10)
    for key in ("valid", "level", "zone_type", "occupied", "capacity",
                "rate", "threshold", "timestamp"):
        assert key in body
    assert body["zone_type"] == "souterrain"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", body["timestamp"])


def test_extra_zone_type_parc_relais():
    assert "parc_relais" in THRESHOLDS
    body = post_validate("parc_relais", 200, 172)  # 86 % -> seuil modere (85)
    assert body["level"] == "moderate"
    assert body["threshold"] == 85
    body = post_validate("parc_relais", 200, 194)  # 97 % -> critique
    assert body["level"] == "critical"
    assert body["threshold"] == 97


def test_zero_capacity_is_invalid():
    body = post_validate("silo", 0, 0)
    assert body["valid"] is False
    assert body["level"] == "invalid"


def test_negative_values_rejected_by_schema():
    response = client.post(
        "/validate", json={"zone_type": "pmr", "capacity": 10, "occupied": -1}
    )
    assert response.status_code == 422


def test_compute_rate_rounding():
    assert compute_rate(1, 3) == 33.3
    assert compute_rate(2, 3) == 66.7


def test_classify_boundaries():
    thresholds = THRESHOLDS["pmr"]  # 60 / 80
    assert classify(59.9, thresholds) == "normal"
    assert classify(60.0, thresholds) == "moderate"
    assert classify(79.9, thresholds) == "moderate"
    assert classify(80.0, thresholds) == "critical"


def test_validate_zone_direct_call():
    data = ParkingZoneData(zone_type="silo", capacity=200, occupied=190)
    result = validate_zone(data)
    assert result["level"] == "critical"
    assert result["rate"] == 95.0
    assert result["threshold"] == 95


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
