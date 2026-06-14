import time
import requests


def test_health_endpoint_returns_healthy(base_url):
    response = requests.get(f"{base_url}/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_register_user_creates_new_user(base_url, user_credentials):
    response = requests.post(f"{base_url}/api/auth/register", json=user_credentials)
    assert response.status_code == 201
    data = response.json()

    assert "user" in data
    assert data["user"]["username"] == user_credentials["username"]


def test_login_returns_jwt_token(base_url, registered_user):
    response = requests.post(f"{base_url}/api/auth/login", json=registered_user)
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["user"]["username"] == registered_user["username"]


def test_create_public_event_requires_auth_and_succeeds_with_token(base_url, auth_headers):
    payload = {
        "title": f"Test Event {int(time.time())}",
        "description": "Integration test event",
        "date": "2026-12-31T18:00:00",
        "location": "Frankfurt",
        "capacity": 50,
        "is_public": True,
        "requires_admin": False,
    }

    response = requests.post(f"{base_url}/api/events", json=payload, headers=auth_headers)
    assert response.status_code == 201
    event = response.json()

    assert event["title"] == payload["title"]
    assert event["date"].startswith("2026-12-31T18:00:00")
    assert event["is_public"] is True
    assert event["requires_admin"] is False


def test_rsvp_public_event_without_auth_succeeds(base_url, auth_headers):
    # 1) Öffentliches Event anlegen (braucht Auth)
    payload = {
        "title": f"Public RSVP Event {int(time.time())}",
        "description": "Public event for RSVP",
        "date": "2026-12-31T18:00:00",
        "location": "Berlin",
        "capacity": 20,
        "is_public": True,
        "requires_admin": False,
    }
    create_response = requests.post(
        f"{base_url}/api/events",
        json=payload,
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    event = create_response.json()
    event_id = event["id"]

    # 2) Ohne Auth auf öffentliches Event RSVP setzen
    rsvp_response = requests.post(
        f"{base_url}/api/rsvps/event/{event_id}",
        json={"attending": True},
    )
    assert rsvp_response.status_code in (200, 201)
    rsvp_data = rsvp_response.json()
    assert rsvp_data["event_id"] == event_id
    assert rsvp_data["attending"] is True


# Fehler-/Grenzfalltests

def test_duplicate_registration_returns_400(base_url, user_credentials):
    first = requests.post(f"{base_url}/api/auth/register", json=user_credentials)
    second = requests.post(f"{base_url}/api/auth/register", json=user_credentials)

    assert first.status_code == 201
    assert second.status_code == 400
    assert "error" in second.json()


def test_create_event_without_auth_returns_401(base_url):
    payload = {
        "title": "Unauthorized Event",
        "description": "Should fail",
        "date": "2026-12-31T18:00:00",
        "location": "Hamburg",
        "capacity": 10,
        "is_public": True,
        "requires_admin": False,
    }
    response = requests.post(f"{base_url}/api/events", json=payload)
    assert response.status_code == 401


def test_rsvp_private_event_without_auth_returns_401(base_url, auth_headers):
    # 1) privates Event erzeugen (braucht Auth)
    payload = {
        "title": f"Private Event {int(time.time())}",
        "description": "Private event",
        "date": "2026-12-31T18:00:00",
        "location": "Munich",
        "capacity": 5,
        "is_public": False,
        "requires_admin": False,
    }
    create_response = requests.post(
        f"{base_url}/api/events",
        json=payload,
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    event = create_response.json()
    event_id = event["id"]

    # 2) Ohne Auth auf privates Event RSVP setzen → sollte 401 liefern
    response = requests.post(
        f"{base_url}/api/rsvps/event/{event_id}",
        json={"attending": True},
    )
    assert response.status_code == 401
    data = response.json()
    assert "Authentication required" in data.get("error", "")