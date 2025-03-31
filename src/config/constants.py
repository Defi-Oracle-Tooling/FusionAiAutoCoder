"""Constants and configuration values."""
from typing import Dict, Any, Final, List
from enum import Enum

# API Configuration
API_VERSION: Final[str] = "v1"
DEFAULT_PORT: Final[int] = 8080
DEFAULT_HOST: Final[str] = "0.0.0.0"
API_TIMEOUT: Final[int] = 30

# Logging Configuration
DEFAULT_LOG_LEVEL: Final[str] = "INFO"
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Agent Configuration
MAX_AGENTS: Final[int] = 4
AGENT_TIMEOUT: Final[int] = 30
DEFAULT_MODEL: Final[str] = "gpt-4"
DEFAULT_TEMPERATURE: Final[float] = 0.7

# Task Configuration
class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Default agent parameters
DEFAULT_AGENT_PARAMS: Final[Dict[str, Any]] = {
    "model": DEFAULT_MODEL,
    "temperature": DEFAULT_TEMPERATURE,
    "max_tokens": 1000,
    "timeout": AGENT_TIMEOUT
}

# Supported languages
SUPPORTED_LANGUAGES: Final[List[str]] = [
    "python",
    "typescript",
    "javascript",
    "java",
    "csharp",
    "cpp",
    "rust"
]

# Cache Configuration
CACHE_ENABLED: Final[bool] = True
CACHE_TTL: Final[int] = 3600  # 1 hour
MAX_CACHE_SIZE: Final[int] = 1000

# Performance Thresholds
CPU_THRESHOLD: Final[float] = 80.0  # percentage
MEMORY_THRESHOLD: Final[float] = 85.0  # percentage
REQUEST_TIMEOUT: Final[int] = 30  # seconds