"""Utility functions for FusionAiAutoCoder."""

from typing import Dict, Any, Optional, Union
import os
import json
from pathlib import Path
import torch  # type: ignore
from datetime import datetime, timezone  # type: ignore
from logging import Logger  # type: ignore
import logging  # type: ignore


def setup_logging(
    level: Optional[str] = None, log_file: Optional[str] = None
) -> Logger:
    """Configure logging for the application."""
    log_level: int = getattr(logging, level or os.environ.get("LOG_LEVEL", "INFO"))

    logger: Logger = logging.getLogger("fusion_ai")
    logger.setLevel(log_level)

    formatter: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def is_gpu_available() -> bool:
    """Check if GPU acceleration is available."""
    if os.environ.get("ENABLE_GPU_ACCELERATION", "").lower() == "false":
        return False
    return torch.cuda.is_available()


def get_gpu_info() -> Dict[str, Any]:
    """Get detailed GPU information if available."""
    info: Dict[str, Any] = {"available": is_gpu_available(), "count": 0, "devices": []}

    if info["available"]:
        info["count"] = torch.cuda.device_count()
        for i in range(info["count"]):
            device_info: Dict[str, Any] = {
                "name": torch.cuda.get_device_name(i),
                "capability": torch.cuda.get_device_capability(i),
                "total_memory": torch.cuda.get_device_properties(i).total_memory,
                "free_memory": torch.cuda.memory_allocated(i),
            }
            info["devices"].append(device_info)

    return info


def get_version_info() -> Dict[str, str]:
    """Get version information for the application."""
    version_file: Path = Path(__file__).parent.parent / "version.json"
    version_info: Dict[str, str] = {
        "version": "0.1.0",
        "build_date": datetime.now(datetime.timezone.utc).isoformat(),
    }

    if version_file.exists():
        with open(version_file) as f:
            version_info.update(json.load(f))

    return version_info


def read_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Read configuration from a JSON file."""
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path) as f:
        config: Dict[str, Any] = json.load(f)

    return config


def save_config(config: Dict[str, Any], config_path: Union[str, Path]) -> None:
    """Save configuration to a JSON file."""
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
