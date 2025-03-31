"""Test multi-agent system functionality."""
from typing import Dict, Any, Optional, List, AsyncGenerator
import pytest
from unittest.mock import MagicMock
import asyncio

from src.config.config_multi_agents import AgentOrchestrator, AgentConfig, AgentRole
from src.types import TaskType, TaskResult, ConfigDict

@pytest.fixture
async def mock_orchestrator() -> AsyncGenerator[AgentOrchestrator, None]:
    """Create a mock orchestrator for testing."""
    config: ConfigDict = {
        "max_agents": 2,
        "timeout_seconds": 5
    }
    orchestrator = AgentOrchestrator(config)
    yield orchestrator

@pytest.mark.asyncio
async def test_agent_initialization(mock_orchestrator: AgentOrchestrator) -> None:
    """Test agent initialization."""
    assert mock_orchestrator.agents
    assert "code_gen" in mock_orchestrator.agents
    
    code_gen: AgentConfig = mock_orchestrator.agents["code_gen"]
    assert code_gen.role == AgentRole.CODE_GENERATOR
    assert isinstance(code_gen.capabilities, list)
    assert "code_generation" in code_gen.capabilities

@pytest.mark.asyncio
async def test_code_generation_workflow(mock_orchestrator: AgentOrchestrator) -> None:
    """Test code generation workflow."""
    task_data: Dict[str, Any] = {
        "prompt": "Create a function to validate email addresses",
        "language": "python",
        "complexity": "medium"
    }
    
    result: Dict[str, Any] = mock_orchestrator.create_workflow(
        TaskType.CODE_GENERATION.value,
        task_data
    )
    assert isinstance(result, dict)

@pytest.mark.asyncio
async def test_code_optimization_workflow(mock_orchestrator: AgentOrchestrator) -> None:
    """Test code optimization workflow."""
    task_data: Dict[str, Any] = {
        "code": "def test(): pass",
        "language": "python",
        "target": "performance"
    }
    
    result: Dict[str, Any] = mock_orchestrator.create_workflow(
        TaskType.CODE_OPTIMIZATION.value,
        task_data
    )
    assert isinstance(result, dict)

@pytest.mark.asyncio
async def test_invalid_task_type(mock_orchestrator: AgentOrchestrator) -> None:
    """Test handling of invalid task type."""
    task_data: Dict[str, Any] = {"test": "data"}
    
    result: Dict[str, Any] = mock_orchestrator.create_workflow(
        "invalid_task_type",
        task_data
    )
    assert "error" in result