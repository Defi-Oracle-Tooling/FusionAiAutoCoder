"""Test batch processing functionality."""
from typing import Dict, Any, List, AsyncGenerator
import pytest
import asyncio
from datetime import datetime

from src.main import run_batch_process, batch_process
from src.types import TaskType, TaskResult, BatchData

@pytest.fixture
def sample_tasks() -> BatchData:
    """Provide sample batch tasks."""
    return [
        {
            "type": TaskType.CODE_GENERATION.value,
            "data": {
                "prompt": "Create a function to validate email",
                "language": "python"
            }
        },
        {
            "type": TaskType.CODE_OPTIMIZATION.value,
            "data": {
                "code": "def test(): pass",
                "target": "performance"
            }
        }
    ]

@pytest.mark.asyncio
async def test_batch_process(sample_tasks: BatchData) -> None:
    """Test asynchronous batch processing."""
    results: List[Dict[str, Any]] = await batch_process(sample_tasks)
    assert isinstance(results, list)
    assert len(results) == len(sample_tasks)
    for result in results:
        assert isinstance(result, dict)

def test_run_batch_process(sample_tasks: BatchData) -> None:
    """Test synchronous batch processing wrapper."""
    results: List[Dict[str, Any]] = run_batch_process(sample_tasks)
    assert isinstance(results, list)
    assert len(results) == len(sample_tasks)
    for result in results:
        assert isinstance(result, dict)

@pytest.mark.asyncio
async def test_batch_process_error_handling() -> None:
    """Test batch processing error handling."""
    invalid_tasks: BatchData = [
        {
            "type": "invalid_task_type",
            "data": {}
        }
    ]
    results: List[Dict[str, Any]] = await batch_process(invalid_tasks)
    assert len(results) == 1
    assert "error" in results[0]