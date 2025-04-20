import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.core.database import SessionLocal
from app.models import User
from app.core.auth_helpers import get_current_user


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def override_get_current_user():
    def mock_get_current_user():
        return User(id="fake-user-id", username="testuser", email="test@example.com")
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user_token():
    return "fake-jwt-token"


def test_create_duplicate_queue_returns_400(client, db_session, user_token):

    response = client.post(
        "/queues/",
        json={"name": "duplicated-queue"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200

    response = client.post(
        "/queues/",
        json={"name": "duplicated-queue"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Queue already exists"
