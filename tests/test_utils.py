"""Test utilities and helper functions."""

import pytest
from pathlib import Path
import tempfile
import logging
from typing import Generator  # type: ignore

from src.utils import (
    setup_logging,
    get_gpu_info,
    get_version_info,
    read_config,
    save_config,
)
from src.types import ConfigDict


def create_temp_file(content: str) -> Generator[Path, None, None]:
    """Create a temporary file with given content."""
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        yield temp_path
    finally:
        temp_path.unlink()


def test_setup_logging() -> None:
    """Test logging setup."""
    logger = setup_logging(level="DEBUG")
    assert logger.level == 10  # DEBUG level

    with tempfile.NamedTemporaryFile(suffix=".log") as tf:
        log_file = Path(tf.name)
        logger = setup_logging(level="INFO", log_file=str(log_file))
        assert logger.level == 20  # INFO level
        assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)


def test_gpu_info() -> None:
    """Test GPU information retrieval."""
    gpu_info: Dict[str, Any] = get_gpu_info()
    assert isinstance(gpu_info, dict)
    assert "available" in gpu_info
    assert isinstance(gpu_info["available"], bool)
    assert isinstance(gpu_info["count"], int)
    assert isinstance(gpu_info["devices"], list)


def test_version_info() -> None:
    """Test version information retrieval."""
    version_info: Dict[str, str] = get_version_info()
    assert isinstance(version_info, dict)
    assert "version" in version_info
    assert isinstance(version_info["version"], str)
    assert "build_date" in version_info


def test_config_operations() -> None:
    """Test configuration file operations."""
    test_config: ConfigDict = {"test_key": "test_value", "nested": {"key": "value"}}

    with create_temp_file("{}") as temp_path:
        # Test saving config
        save_config(test_config, temp_path)

        # Test reading config
        loaded_config: ConfigDict = read_config(temp_path)
        assert loaded_config == test_config

        # Test reading non-existent file
        with pytest.raises(FileNotFoundError):
            read_config("non_existent_file.json")
