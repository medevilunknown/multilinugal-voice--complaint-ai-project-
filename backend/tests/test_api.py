"""
Backend test suite for the CyberGuard AI API.
Tests core endpoints: health, root, chat, and complaint creation.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app  # noqa: E402

# ─── Test Database Setup ────────────────────────────────────────────────
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_cyberguard.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    # Setup
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


# ─── Health & Root ──────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_root_returns_languages(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "supported_languages" in data
        assert "English" in data["supported_languages"]
        assert "Hindi" in data["supported_languages"]
        assert len(data["supported_languages"]) >= 20


# ─── Chat Endpoint ──────────────────────────────────────────────────────

class TestChatEndpoint:
    def test_chat_requires_message(self, client):
        response = client.post("/chat", json={
            "session_id": "test-session-001",
            "language": "English",
        })
        assert response.status_code == 422  # Validation error — message is required

    def test_chat_returns_response(self, client):
        response = client.post("/chat", json={
            "session_id": "test-session-002",
            "language": "English",
            "message": "Hello",
        })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

    def test_chat_returns_session_id(self, client):
        response = client.post("/chat", json={
            "session_id": "test-session-003",
            "language": "English",
            "message": "I lost money on Google Pay",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-003"


# ─── Complaint Endpoint ─────────────────────────────────────────────────

class TestComplaintEndpoint:
    def test_create_complaint_validation(self, client):
        """Ensure incomplete payloads are rejected."""
        response = client.post("/complaint/create", json={
            "full_name": "Test User",
            # Missing required fields
        })
        assert response.status_code == 422

    @pytest.mark.skip(reason="Requires live Gemini API Key. Flaky in CI/CD environments.")
    def test_create_complaint_success(self, client):
        """Full complaint submission should return a ticket ID."""
        response = client.post("/complaint/create", json={
            "full_name": "Rohit Kumar",
            "phone_number": "9876543210",
            "email": "rohit@example.com",
            "address": "123 Main St, Mumbai",
            "complaint_type": "UPI / Payment Fraud",
            "date_time": "2026-03-25 11:58",
            "description": "Lost 5000 rupees on Google Pay to a scammer UPI ID",
            "amount_lost": "5000",
            "platform": "Google Pay",
            "language": "English",
        })
        assert response.status_code == 200
        data = response.json()
        assert "ticket_id" in data
        assert data["ticket_id"].startswith("CG-")
