"""Input validation and type checking utilities."""

from typing import Dict, Any, List, Optional, Type, TypeVar, Union  # type: ignore
from pathlib import Path
import re

from src.config.constants import SUPPORTED_LANGUAGES, TaskPriority, TaskStatus
from src.types import ConfigurationError

T = TypeVar("T")


def validate_language(language: str) -> str:
    """Validate programming language is supported."""
    if language.lower() not in SUPPORTED_LANGUAGES:
        raise ConfigurationError(
            f"Unsupported language: {language}. Supported languages: {SUPPORTED_LANGUAGES}"
        )
    return language.lower()


def validate_priority(priority: str) -> TaskPriority:
    """Validate task priority."""
    try:
        return TaskPriority(priority.lower())
    except ValueError:
        raise ConfigurationError(
            f"Invalid priority: {priority}. Valid priorities: {[p.value for p in TaskPriority]}"
        )


def validate_status(status: str) -> TaskStatus:
    """Validate task status."""
    try:
        return TaskStatus(status.lower())
    except ValueError:
        raise ConfigurationError(
            f"Invalid status: {status}. Valid statuses: {[s.value for s in TaskStatus]}"
        )


def validate_file_path(path: Union[str, Path]) -> Path:
    """Validate file path."""
    try:
        path = Path(path)
        if not path.parent.exists():
            raise ConfigurationError(f"Parent directory does not exist: {path.parent}")
        return path
    except Exception as e:
        raise ConfigurationError(f"Invalid file path: {path}") from e


def validate_type(value: Any, expected_type: Type[T]) -> T:
    """Validate value is of expected type."""
    if not isinstance(value, expected_type):
        raise ConfigurationError(
            f"Invalid type: {type(value)}. Expected: {expected_type}"
        )
    return value


def validate_email(email: str) -> str:
    """Validate email address format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ConfigurationError(f"Invalid email format: {email}")
    return email


def validate_port(port: int) -> int:
    """Validate port number."""
    if not 0 <= port <= 65535:
        raise ConfigurationError(f"Invalid port number: {port}")
    return port


def validate_config(config: Dict[str, Any], required_keys: List[str]) -> Dict[str, Any]:
    """Validate configuration dictionary has required keys."""
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ConfigurationError(f"Missing required configuration keys: {missing_keys}")
    return config
