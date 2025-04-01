"""Test PyTorch installation and GPU functionality."""

from typing import Dict, Any
import pytest  # type: ignore
import numpy as np  # type: ignore
from numpy.testing import assert_array_equal  # type: ignore
from numpy.typing import NDArray  # type: ignore

from src.utils import is_gpu_available, get_gpu_info

import torch  # type: ignore
import torchvision  # type: ignore
import torchaudio  # type: ignore


def test_torch_import() -> None:
    """Test that PyTorch can be imported."""
    assert torch.__version__
    assert hasattr(torch, "cuda")


def test_basic_operations() -> tuple[torch.Tensor, NDArray[Any]]:
    """Test basic PyTorch operations."""
    x: torch.Tensor = torch.rand(5, 3)
    y: torch.Tensor = torch.rand(5, 3)
    z: torch.Tensor = x + y
    numpy_array: NDArray[Any] = z.numpy()
    return z, numpy_array


def test_numpy_interop() -> None:
    """Test NumPy interoperability."""
    numpy_array: np.ndarray = np.random.rand(5, 3)
    tensor: torch.Tensor = torch.from_numpy(numpy_array)
    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (5, 3)

    back_to_numpy: np.ndarray = tensor.numpy()
    assert isinstance(back_to_numpy, np.ndarray)
    np.testing.assert_array_equal(numpy_array, back_to_numpy)


def test_gpu_detection() -> None:
    """Test GPU detection functionality."""
    gpu_available: bool = is_gpu_available()
    assert isinstance(gpu_available, bool)

    gpu_info: Dict[str, Any] = get_gpu_info()
    assert isinstance(gpu_info["available"], bool)
    assert isinstance(gpu_info["count"], int)
    assert gpu_info["available"] == gpu_available


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_gpu_operations() -> None:
    """Test GPU tensor operations."""
    x: torch.Tensor = torch.rand(5, 3).cuda()
    y: torch.Tensor = torch.rand(5, 3).cuda()

    z: torch.Tensor = x + y
    assert z.is_cuda
    assert z.shape == (5, 3)

    cpu_tensor: torch.Tensor = z.cpu()
    assert not cpu_tensor.is_cuda
