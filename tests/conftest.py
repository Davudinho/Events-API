import time
import pytest
import requests

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def unique_username():
    # sorgt für eindeutige Usernamen pro Testlauf
    return f"testuser_{int(time.time() * 1000)}"


@pytest.fixture
def user_credentials(unique_username):
    return {
        "username": unique_username,
        "password": "TestPassword123!"
    }


@pytest.fixture
def registered_user(base_url, user_credentials):
    response = requests.post(f"{base_url}/api/auth/register", json=user_credentials)
    assert response.status_code == 201
    return user_credentials


@pytest.fixture
def auth_token(base_url, registered_user):
    response = requests.post(f"{base_url}/api/auth/login", json=registered_user)
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}