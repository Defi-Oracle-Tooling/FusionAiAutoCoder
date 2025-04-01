"""Type definitions for FusionAiAutoCoder."""

from typing import TypeVar, Dict, Any, Union, List, Optional, TypedDict
from enum import Enum
import torch  # type: ignore
import numpy as np
from datetime import datetime
import os


class TaskType(Enum):
    """Enumeration of possible task types."""

    CODE_GENERATION = "code_generation"
    CODE_OPTIMIZATION = "code_optimization"
    CODE_REVIEW = "code_review"
    TEST_GENERATION = "test_generation"


class GPUCheckResult(Enum):
    """Enumeration of possible GPU check results."""

    AVAILABLE = "available"
    NOT_AVAILABLE = "not_available"
    ERROR = "error"


class OptimizationTarget(Enum):
    """Enumeration of optimization targets."""

    PERFORMANCE = "performance"
    MEMORY = "memory"
    READABILITY = "readability"


class TorchVersionInfo(TypedDict):
    """Data class for PyTorch version information."""

    torch_version: str
    torchvision_version: str
    torchaudio_version: str
    cuda_available: bool
    device_info: Dict[str, Union[str, int, bool]]


class TaskResult(TypedDict):
    """Data class for task execution results."""

    task_id: str
    status: str
    result: Dict[str, Any]
    execution_time: float
    timestamp: datetime
    error: Optional[str]


class TorchInstallError(Exception):
    """Custom exception for PyTorch installation issues."""

    def __init__(self, message: str, error_code: int = 1) -> None:
        self.error_code: int = error_code
        super().__init__(message)


class ConfigurationError(Exception):
    """Custom exception for configuration issues."""

    def __init__(self, message: str, config_key: Optional[str] = None) -> None:
        self.config_key: Optional[str] = config_key
        super().__init__(message)


# Type aliases
TensorOrArray = Union[torch.Tensor, np.ndarray[Any, Any]]  # Represents a tensor or numpy array
BatchData = List[Dict[str, Any]]
ModelOutput = TypeVar("ModelOutput")  # Generic type for model outputs
ConfigDict = Dict[str, Any]
JsonDict = Dict[str, Any]
PathLike = Union[str, bytes, "os.PathLike[str]", "os.PathLike[bytes]"]
