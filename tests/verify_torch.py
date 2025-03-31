import torch
import torchvision
import torchaudio

def print_torch_info():
    print(f"PyTorch Version: {torch.__version__}")
    print(f"TorchVision Version: {torchvision.__version__}")
    print(f"TorchAudio Version: {torchaudio.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
    else:
        print("Running on CPU")
    
    # Quick tensor operation test
    x = torch.rand(5, 3)
    print("\nTest Tensor:")
    print(x)

if __name__ == "__main__":
    print_torch_info()