"""Test validation utilities."""
from typing import Dict, Any, List
import pytest
from pathlib import Path

from src.validation import (
    validate_language,
    validate_priority,
    validate_status,
    validate_file_path,
    validate_type,
    validate_email,
    validate_port,
    validate_config
)
from src.types import ConfigurationError
from src.config.constants import TaskPriority, TaskStatus

def test_validate_language() -> None:
    """Test language validation."""
    assert validate_language("python") == "python"
    assert validate_language("PYTHON") == "python"
    
    with pytest.raises(ConfigurationError):
        validate_language("invalid_language")

def test_validate_priority() -> None:
    """Test priority validation."""
    assert validate_priority("high") == TaskPriority.HIGH
    assert validate_priority("LOW") == TaskPriority.LOW
    
    with pytest.raises(ConfigurationError):
        validate_priority("invalid_priority")

def test_validate_status() -> None:
    """Test status validation."""
    assert validate_status("pending") == TaskStatus.PENDING
    assert validate_status("COMPLETED") == TaskStatus.COMPLETED
    
    with pytest.raises(ConfigurationError):
        validate_status("invalid_status")

def test_validate_file_path(tmp_path: Path) -> None:
    """Test file path validation."""
    test_file: Path = tmp_path / "test.txt"
    test_file.touch()
    
    assert validate_file_path(test_file) == test_file
    assert validate_file_path(str(test_file)) == test_file
    
    with pytest.raises(ConfigurationError):
        validate_file_path("/nonexistent/path/file.txt")

def test_validate_type() -> None:
    """Test type validation."""
    assert validate_type("test", str) == "test"
    assert validate_type(123, int) == 123
    
    with pytest.raises(ConfigurationError):
        validate_type("test", int)

def test_validate_email() -> None:
    """Test email validation."""
    valid_emails: List[str] = [
        "test@example.com",
        "user.name@domain.co.uk",
        "user+label@example.com"
    ]
    
    invalid_emails: List[str] = [
        "invalid_email",
        "@domain.com",
        "user@",
        "user@.com"
    ]
    
    for email in valid_emails:
        assert validate_email(email) == email
    
    for email in invalid_emails:
        with pytest.raises(ConfigurationError):
            validate_email(email)

def test_validate_port() -> None:
    """Test port validation."""
    assert validate_port(8080) == 8080
    assert validate_port(1) == 1
    assert validate_port(65535) == 65535
    
    with pytest.raises(ConfigurationError):
        validate_port(-1)
    with pytest.raises(ConfigurationError):
        validate_port(65536)

def test_validate_config() -> None:
    """Test configuration validation."""
    config: Dict[str, Any] = {
        "key1": "value1",
        "key2": "value2"
    }
    
    # Test with existing keys
    assert validate_config(config, ["key1"]) == config
    assert validate_config(config, ["key1", "key2"]) == config
    
    # Test with missing keys
    with pytest.raises(ConfigurationError):
        validate_config(config, ["key1", "missing_key"])