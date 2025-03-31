from typing import Dict, Any
import torch
import torchvision  # type: ignore
import torchaudio  # type: ignore
import numpy as np
from src.types import TorchVersionInfo, TensorOrArray, TorchInstallError, GPUCheckResult


def get_version_info() -> TorchVersionInfo:
    """Get version information for PyTorch and related packages."""
    device_info = {
        "cuda_available": torch.cuda.is_available(),
        "device_name": (
            torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
        ),
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
    }

    return TorchVersionInfo(
        torch_version=torch.__version__,
        torchvision_version=torchvision.__version__,
        torchaudio_version=torchaudio.__version__,
        cuda_available=device_info["cuda_available"],
        device_info=device_info,
    )


def test_basic_operations() -> tuple[TensorOrArray, TensorOrArray]:
    """Test basic PyTorch operations."""
    x: torch.Tensor = torch.rand(5, 3)
    y: torch.Tensor = torch.rand(5, 3)
    z: torch.Tensor = x + y
    numpy_array: np.ndarray = z.numpy()
    return z, numpy_array


def test_gpu_availability() -> GPUCheckResult:
    """Check GPU availability and specifications."""
    try:
        if torch.cuda.is_available():
            # Test CUDA capabilities
            x: torch.Tensor = torch.rand(5, 3).cuda()
            return GPUCheckResult.AVAILABLE
        return GPUCheckResult.NOT_AVAILABLE
    except Exception:
        return GPUCheckResult.ERROR


def test_torch_installation() -> bool:
    """Verify PyTorch installation and basic functionality."""
    try:
        # Get versions
        version_info: TorchVersionInfo = get_version_info()
        print(f"PyTorch Version: {version_info.torch_version}")
        print(f"TorchVision Version: {version_info.torchvision_version}")
        print(f"TorchAudio Version: {version_info.torchaudio_version}")

        # Test operations
        tensor, array = test_basic_operations()
        if not isinstance(tensor, (torch.Tensor, np.ndarray)):
            raise TorchInstallError("Failed tensor operation test")

        # Check GPU
        gpu_status: GPUCheckResult = test_gpu_availability()
        print(f"CUDA Available: {version_info.cuda_available}")
        print(f"Device: {version_info.device_info['device_name']}")

        return True
    except Exception as e:
        print(f"PyTorch Installation Test Failed: {str(e)}")
        return False


if __name__ == "__main__":
    success: bool = test_torch_installation()
    print(f"PyTorch Installation Test: {'✅ PASSED' if success else '❌ FAILED'}")
