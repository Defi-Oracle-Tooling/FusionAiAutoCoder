h
#!/bin/bash
set -e

echo "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

echo "Installing required dependencies..."
sudo apt-get install -y curl python3 python3-pip

echo "Installing VS Code Insiders..."
curl -L -o vscode-insiders.deb "https://update.code.visualstudio.com/latest/linux-deb-x64/insider"
sudo dpkg -i vscode-insiders.deb || sudo apt-get install -f -y

echo "Installing ONNX Runtime..."
pip3 install onnxruntime

# If an Ollama installer is available for Linux,
# add installation instructions here

echo "Installing AutoGen..."
pip3 install autogen

echo "Setup complete. Please install the AI Toolkit plugin from VS Code Insiders."