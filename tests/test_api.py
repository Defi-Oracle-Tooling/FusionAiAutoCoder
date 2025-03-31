"""
Unit tests for the API layer.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import uuid

from src.api import app

client = TestClient(app)

@pytest.fixture
def mock_hybrid_workflow():
    """Fixture to mock the hybrid_workflow function."""
    with patch('src.api.hybrid_workflow') as mock:
        # Configure the mock to return a predefined result
        def mock_workflow(task_type, task_data):
            if task_type == "code_generation":
                return {
                    "code": "def validate_email(email):\n    # Implementation\n    pass",
                    "language": task_data.get("language", "python"),
                    "confidence": 0.85,
                    "metadata": {
                        "execution_time": 1.23,
                        "gpu_used": task_data.get("use_gpu", False)
                    }
                }
            elif task_type == "code_optimization":
                return {
                    "optimized_code": "def optimized_function():\n    pass",
                    "language": task_data.get("language", "python"),
                    "improvements": ["Algorithm optimization", "Memory usage reduction"],
                    "estimated_speedup": "75%",
                    "metadata": {
                        "execution_time": 2.34,
                        "gpu_used": False
                    }
                }
            else:
                return {"error": "Unknown task type"}
        
        mock.side_effect = mock_workflow
        yield mock

@pytest.fixture
def mock_batch_process():
    """Fixture to mock the batch_process function."""
    with patch('src.api.batch_process') as mock:
        # Configure the mock to return a list of results
        mock.return_value = [
            {
                "code": "def function1():\n    pass",
                "language": "python",
                "confidence": 0.8
            },
            {
                "optimized_code": "def optimized_function():\n    pass",
                "language": "python",
                "improvements": ["Algorithm optimization"]
            }
        ]
        yield mock

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime" in data

def test_create_task(mock_hybrid_workflow):
    """Test the create_task endpoint."""
    request_data = {
        "task_type": "code_generation",
        "task_data": {
            "prompt": "Create a sorting function",
            "language": "python"
        }
    }
    
    response = client.post("/api/task", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"

def test_get_task():
    """Test the get_task endpoint."""
    # First create a task
    request_data = {
        "task_type": "code_generation",
        "task_data": {
            "prompt": "Create a sorting function",
            "language": "python"
        }
    }
    
    create_response = client.post("/api/task", json=request_data)
    task_id = create_response.json()["task_id"]
    
    # Then get the task
    response = client.get(f"/api/task/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    
    # Test with non-existent task ID
    response = client.get(f"/api/task/{uuid.uuid4()}")
    assert response.status_code == 404

def test_generate_code(mock_hybrid_workflow):
    """Test the generate_code endpoint."""
    request_data = {
        "prompt": "Create a sorting function",
        "language": "python",
        "complexity": "medium",
        "use_gpu": True
    }
    
    response = client.post("/api/generate", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"
    
    # Verify that hybrid_workflow was called with the right parameters
    mock_hybrid_workflow.assert_called_once()
    args, kwargs = mock_hybrid_workflow.call_args
    assert args[0] == "code_generation"
    assert args[1]["prompt"] == "Create a sorting function"
    assert args[1]["language"] == "python"
    assert args[1]["complexity"] == "medium"
    assert args[1]["use_gpu"] is True

def test_optimize_code(mock_hybrid_workflow):
    """Test the optimize_code endpoint."""
    request_data = {
        "code": "def sort(arr):\n    return sorted(arr)",
        "optimization_target": "performance",
        "language": "python"
    }
    
    response = client.post("/api/optimize", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"
    
    # Verify that hybrid_workflow was called with the right parameters
    mock_hybrid_workflow.assert_called_once()
    args, kwargs = mock_hybrid_workflow.call_args
    assert args[0] == "code_optimization"
    assert "code" in args[1]
    assert args[1]["optimization_target"] == "performance"
    assert args[1]["language"] == "python"

def test_batch_tasks(mock_batch_process):
    """Test the batch_tasks endpoint."""
    request_data = {
        "tasks": [
            {
                "task_type": "code_generation",
                "task_data": {
                    "prompt": "Create a sorting function",
                    "language": "python"
                }
            },
            {
                "task_type": "code_optimization",
                "task_data": {
                    "code": "def sort(arr):\n    return sorted(arr)",
                    "optimization_target": "performance"
                }
            }
        ]
    }
    
    response = client.post("/api/batch", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert all("task_id" in item for item in data)
    assert all(item["status"] == "completed" for item in data)
    
    # Verify that batch_process was called with the right parameters
    mock_batch_process.assert_called_once()
    args, kwargs = mock_batch_process.call_args
    assert len(args[0]) == 2
    assert args[0][0]["task_type"] == "code_generation"
    assert args[0][1]["task_type"] == "code_optimization"