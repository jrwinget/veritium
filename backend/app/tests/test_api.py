import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db, Base
import tempfile
import os

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

class TestDocumentEndpoints:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Veritium API" in response.json()["message"]

    def test_upload_document_no_file(self, client):
        response = client.post("/api/v1/documents/upload")
        assert response.status_code == 400

    def test_upload_from_invalid_url(self, client):
        response = client.post(
            "/api/v1/documents/upload",
            data={"url": "not-a-url"}
        )
        assert response.status_code == 400

    def test_upload_from_invalid_doi(self, client):
        response = client.post(
            "/api/v1/documents/upload",
            data={"doi": "invalid-doi"}
        )
        assert response.status_code == 400

    def test_get_nonexistent_document(self, client):
        response = client.get("/api/v1/documents/99999")
        assert response.status_code == 404

    def test_list_documents_empty(self, client):
        response = client.get("/api/v1/documents/")
        assert response.status_code == 200
        assert response.json() == []

class TestAssessmentEndpoints:
    def test_create_assessment_invalid_document(self, client):
        response = client.post(
            "/api/v1/assessments/",
            json={
                "document_id": 99999,
                "user_claim": "Test claim"
            }
        )
        assert response.status_code in [400, 404]  # Should fail for non-existent document

    def test_get_nonexistent_assessment(self, client):
        response = client.get("/api/v1/assessments/99999")
        assert response.status_code == 404

    def test_get_nonexistent_shared_assessment(self, client):
        response = client.get("/api/v1/assessments/share/invalid-share-id")
        assert response.status_code == 404

    def test_submit_feedback_invalid_assessment(self, client):
        response = client.post(
            "/api/v1/assessments/99999/feedback",
            json={
                "feedback_score": 1,
                "feedback_comment": "Test comment"
            }
        )
        assert response.status_code == 404