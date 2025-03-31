"""
Unit tests for the main module.
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock

from src.main import hybrid_workflow, batch_process

# Test data
TEST_TASK_CODE_GENERATION = {
    "prompt": "Create a function to validate email addresses",
    "language": "python",
    "complexity": "low",
}

TEST_TASK_CODE_OPTIMIZATION = {
    "code": "def factorial(n):\n    if n == 0: return 1\n    return n * factorial(n-1)",
    "optimization_target": "performance",
    "language": "python",
}


@pytest.fixture
def mock_setup_agents():
    """Fixture to mock the setup_agents function."""
    with patch("src.main.setup_agents") as mock:
        # Create a mock agent orchestrator
        mock_orchestrator = MagicMock()

        # Configure the mock to return a predefined result
        def mock_workflow(task_type, task_data):
            if task_type == "code_generation":
                return {
                    "code": "def validate_email(email):\n    # Implementation\n    pass",
                    "language": "python",
                    "confidence": 0.85,
                }
            elif task_type == "code_optimization":
                return {
                    "optimized_code": "def factorial(n):\n    result = 1\n    for i in range(1, n+1):\n        result *= i\n    return result",
                    "language": "python",
                    "improvements": ["Recursive to iterative", "Reduced stack usage"],
                    "estimated_speedup": "50%",
                }
            else:
                return {"error": "Unknown task type"}

        mock_orchestrator.create_workflow.side_effect = mock_workflow
        mock.return_value = mock_orchestrator
        yield mock


@pytest.fixture
def mock_gpu_available():
    """Fixture to mock the is_gpu_available function."""
    with patch("src.main.is_gpu_available", return_value=True) as mock:
        yield mock


@pytest.fixture
def mock_get_version_info():
    """Fixture to mock the get_version_info function."""
    with patch("src.main.get_version_info") as mock:
        mock.return_value = {"system": "Linux", "python": "3.9.5", "fusion_ai": "1.0.0"}
        yield mock


def test_hybrid_workflow_code_generation(
    mock_setup_agents, mock_gpu_available, mock_get_version_info
):
    """Test the hybrid_workflow function for code generation."""
    # Call the function under test
    result = hybrid_workflow("code_generation", TEST_TASK_CODE_GENERATION)

    # Assertions
    assert result is not None
    assert "code" in result
    assert "language" in result
    assert "confidence" in result
    assert "metadata" in result
    assert result["language"] == "python"
    assert result["metadata"]["gpu_used"] is True


def test_hybrid_workflow_code_optimization(
    mock_setup_agents, mock_gpu_available, mock_get_version_info
):
    """Test the hybrid_workflow function for code optimization."""
    # Call the function under test
    result = hybrid_workflow("code_optimization", TEST_TASK_CODE_OPTIMIZATION)

    # Assertions
    assert result is not None
    assert "optimized_code" in result
    assert "language" in result
    assert "improvements" in result
    assert "estimated_speedup" in result
    assert "metadata" in result
    assert result["language"] == "python"
    assert result["metadata"]["gpu_used"] is True


def test_hybrid_workflow_error_handling(mock_setup_agents):
    """Test error handling in the hybrid_workflow function."""
    # Configure mock to raise an exception
    mock_setup_agents.return_value.create_workflow.side_effect = Exception("Test error")

    # Call the function under test
    result = hybrid_workflow("code_generation", TEST_TASK_CODE_GENERATION)

    # Assertions
    assert result is not None
    assert "error" in result
    assert "metadata" in result
    assert result["metadata"]["success"] is False


def test_batch_process(mock_setup_agents, mock_gpu_available, mock_get_version_info):
    """Test the batch_process function."""
    # Prepare test data
    tasks = [
        {"task_type": "code_generation", "task_data": TEST_TASK_CODE_GENERATION},
        {"task_type": "code_optimization", "task_data": TEST_TASK_CODE_OPTIMIZATION},
    ]

    # Call the function under test
    results = batch_process(tasks)

    # Assertions
    assert results is not None
    assert len(results) == 2
    assert "code" in results[0]
    assert "optimized_code" in results[1]

    # Test with missing task_type
    tasks = [{"task_data": TEST_TASK_CODE_GENERATION}]
    results = batch_process(tasks)
    assert results is not None
    assert len(results) == 1
    assert "error" in results[0]


@pytest.mark.asyncio
async def test_azure_foundry_code_generation(mock_setup_agents) -> None:
    """Test Azure Foundry code generation integration."""
    result = await mock_setup_agents.create_workflow(
        task_type="code_generation",
        task_data={
            "prompt": "Create a function to validate email addresses",
            "language": "python",
        },
    )
    assert "code" in result
    assert result["language"] == "python"


@pytest.mark.asyncio
async def test_azure_foundry_code_optimization(mock_setup_agents) -> None:
    """Test Azure Foundry code optimization integration."""
    result = await mock_setup_agents.create_workflow(
        task_type="code_optimization",
        task_data={"code": "def test(): pass", "target": "performance"},
    )
    assert "optimized_code" in result
    assert result["language"] == "python"
