"""
    test_run contains limited test cases required implemented for urbo application backend service api
"""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from urbo_api.db_connect.db import get_db
from urbo_api.urbo_app_main import app
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Fetch the database URL from environment variables
db_url = os.getenv("DATABASE_URL")
SQLALCHEMY_DATABASE_URL = db_url

# Create SQLAlchemy engine for connecting to the test database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session local class for handling database sessions
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ------------------------- FIXTURES -------------------------

@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


# Mock the API response fixture
@pytest.fixture
def here_api_response():
    return {
        'items': [
            {
                'position': {
                    'lat': 37.7749,
                    'lng': -122.4194
                }
            }
        ]
    }


# Fixture for a successful geocode payload
@pytest.fixture
def geocode_payload():
    return {
        "address": "San Francisco, CA"
    }


# ------------------------- TESTS -------------------------

# Test: Root endpoint
def test_root(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == "Welcome to URBO"


# Test: Successful geocode lookup
def test_get_geocode_success(test_client, geocode_payload, here_api_response):
    # Mock requests.get to return a successful response
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = here_api_response

        # Make the API request
        response = test_client.post("/geocode", json=geocode_payload)

        # Assert the status code and returned data
        assert response.status_code == 200
        response_json = response.json()
        assert response_json['address'] == geocode_payload["address"]
        assert response_json['latitude'] == 37.7749
        assert response_json['longitude'] == -122.4194
        assert "geocode_response" in response_json


# Test: Address not found in HERE API
def test_get_geocode_address_not_found(test_client, geocode_payload):
    # Mock requests.get to return an empty list
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'items': []}

        # Make the API request
        response = test_client.post("/geocode", json=geocode_payload)

        # Assert 404 error for address not found
        assert response.status_code == 404
        response_json = response.json()
        assert response_json['detail'] == "Address not found"


# Test: HERE API returns non-200 status code
def test_get_geocode_here_api_error(test_client, geocode_payload):
    # Mock requests.get to return an error status
    with patch('requests.get') as mock_get:
        # Service Unavailable
        mock_get.return_value.status_code = 503

        # Make the API request
        response = test_client.post("/geocode", json=geocode_payload)

        # Assert that it raises the appropriate HTTPException
        assert response.status_code == 503
        response_json = response.json()
        assert response_json['detail'] == "Error fetching geocode"


# Test: Invalid payload (missing address)
def test_get_geocode_invalid_payload(test_client):
    # Send a request with an invalid payload
    response = test_client.post("/geocode", json={})

    # Assert that it raises a validation error
    assert response.status_code == 422
