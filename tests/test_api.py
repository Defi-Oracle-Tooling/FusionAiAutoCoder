"""API testing module."""

from typing import Dict, Any
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from src.api import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_hybrid_workflow() -> MagicMock:
    """Fixture to mock the hybrid_workflow function."""
    with patch("src.main.hybrid_workflow") as mock:

        async def mock_workflow(
            task_type: str, task_data: Dict[str, Any]
        ) -> Dict[str, Any]:
            if task_type == "code_generation":
                return {
                    "code": "def validate_email(email: str) -> bool:\n    # Implementation\n    pass",
                    "language": task_data.get("language", "python"),
                    "confidence": 0.85,
                    "metadata": {
                        "execution_time": 1.23,
                        "gpu_used": task_data.get("use_gpu", False),
                    },
                }
            elif task_type == "code_optimization":
                return {
                    "optimized_code": "def optimized_function() -> None:\n    pass",
                    "language": task_data.get("language", "python"),
                    "improvements": [
                        "Algorithm optimization",
                        "Memory usage reduction",
                    ],
                    "estimated_speedup": "75%",
                    "metadata": {"execution_time": 2.34, "gpu_used": False},
                }
            else:
                return {"error": "Unknown task type"}

        mock.side_effect = mock_workflow
        yield mock


def test_read_main(client: TestClient) -> None:
    """Test the main endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data: Dict[str, Any] = response.json()
    assert data["status"] == "healthy"
    assert isinstance(data["version"], str)


@pytest.mark.asyncio
async def test_generate_code(
    client: TestClient, mock_hybrid_workflow: MagicMock
) -> None:
    """Test code generation endpoint."""
    response = client.post(
        "/api/v1/generate",
        json={
            "prompt": "Create a function to validate email addresses",
            "language": "python",
        },
    )
    assert response.status_code == 200
    data: Dict[str, Any] = response.json()
    assert "code" in data
    assert "language" in data
    assert data["language"] == "python"
    assert isinstance(data["metadata"], dict)


@pytest.mark.asyncio
async def test_optimize_code(
    client: TestClient, mock_hybrid_workflow: MagicMock
) -> None:
    """Test code optimization endpoint."""
    response = client.post(
        "/api/v1/optimize",
        json={
            "code": "def test(): pass",
            "language": "python",
            "target": "performance",
        },
    )
    assert response.status_code == 200
    data: Dict[str, Any] = response.json()
    assert "optimized_code" in data
    assert "improvements" in data
    assert isinstance(data["improvements"], list)
    assert "estimated_speedup" in data
