"""Tests pytest du validateur d'occupation de stationnement (MS7)."""
from fastapi.testclient import TestClient

from src.validator import THRESHOLDS, app

client = TestClient(app)


def post_validate(zone_type, capacity, occupied):
    response = client.post(
        "/validate",
        json={"zone_type": zone_type, "capacity": capacity, "occupied": occupied},
    )
    assert response.status_code == 200
    return response.json()


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


def test_extra_zone_type_parc_relais():
    assert "parc_relais" in THRESHOLDS
    body = post_validate("parc_relais", 200, 172)
    assert body["level"] == "moderate"


def test_zero_capacity_is_invalid():
    body = post_validate("silo", 0, 0)
    assert body["level"] == "invalid"


def test_health():
    assert client.get("/health").json() == {"status": "ok"}
