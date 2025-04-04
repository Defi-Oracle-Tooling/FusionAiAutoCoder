"""Shared test configuration and fixtures."""

from typing import AsyncGenerator  # Only keep necessary imports
import pytest  # type: ignore
from pathlib import Path
from datetime import datetime, timezone

from src.types import ConfigDict, TaskResult
from src.config.config_multi_agents import AgentOrchestrator


@pytest.fixture
def test_config() -> ConfigDict:
    """Provide test configuration."""
    return {
        "api": {"version": "1.0.0", "port": 8080, "host": "0.0.0.0"},
        "logging": {"level": "DEBUG", "file": "tests.log"},
        "agents": {"max_concurrent": 4, "timeout_seconds": 30},
    }


@pytest.fixture
def sample_task_result() -> TaskResult:
    """Provide a sample task result."""
    return TaskResult(
        task_id="test-123",
        status="completed",
        result={"code": "def test(): pass"},
        execution_time=1.23,
        timestamp=datetime.now(timezone.utc),
    )


@pytest.fixture
async def agent_orchestrator() -> AsyncGenerator[AgentOrchestrator, None]:
    """Provide a configured agent orchestrator."""
    orchestrator = AgentOrchestrator({"max_agents": 2, "timeout_seconds": 10})
    yield orchestrator


@pytest.fixture
def test_data_dir() -> Path:
    """Provide path to test data directory."""
    return Path(__file__).parent / "data"
