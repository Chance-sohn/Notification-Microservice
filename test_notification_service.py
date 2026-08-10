import pytest

from notification_service import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    return app.test_client()


def test_normal_notification(client):
    response = client.post(
        "/notification",
        json={"current": 500, "limit": 1000},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["level"] == "normal"
    assert data["percentage"] == 50.0


def test_warning_notification(client):
    response = client.post(
        "/notification",
        json={"current": 850, "limit": 1000},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["level"] == "warning"
    assert data["percentage"] == 85.0


def test_over_budget_notification(client):
    response = client.post(
        "/notification",
        json={"current": 1200, "limit": 1000},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["level"] == "alert"
    assert data["remaining"] == 0


def test_invalid_limit(client):
    response = client.post(
        "/notification",
        json={"current": 100, "limit": 0},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()
