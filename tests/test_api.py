"""
Automated Integration Tests for FastAPI Backend Endpoints.
Verifies REST response status, schemas, and payload contents.
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert "edge_gateway_sync" in data


def test_api_topology():
    response = client.get("/api/topology")
    assert response.status_code == 200
    data = response.json()
    assert "grid" in data
    assert "feeders" in data
    assert len(data["feeders"]) == 7


def test_api_overview():
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert "baseline_summary" in data
    assert "optimized_summary" in data
    assert "verified_impact" in data
    assert data["verified_impact"]["production_constraint_satisfied"] is True


def test_api_machines():
    response = client.get("/api/machines?view=baseline")
    assert response.status_code == 200
    machines = response.json()
    assert len(machines) == 7
    assert all("sec_kwh_per_unit" in m for m in machines)


def test_api_recommendations():
    response = client.get("/api/recommendations")
    assert response.status_code == 200
    recs = response.json()
    assert isinstance(recs, list)
    assert len(recs) > 0
    assert "operator_action" in recs[0]
