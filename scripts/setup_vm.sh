#!/bin/bash
# VM Setup Script for FusionAiAutoCoder Development Environment

set -e

echo "Setting up development environment for FusionAiAutoCoder..."

# Update package lists
sudo apt-get update

# Install basic dependencies
sudo apt-get install -y \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    git \
    wget \
    unzip \
    python3-pip \
    python3-venv

# Install Docker
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install NVIDIA drivers and CUDA toolkit for GPU support
echo "Installing NVIDIA drivers and CUDA toolkit..."
sudo apt-get install -y nvidia-driver-535 nvidia-cuda-toolkit

# Install kubectl
echo "Installing kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install Azure CLI
echo "Installing Azure CLI..."
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Terraform
echo "Installing Terraform..."
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install terraform

# Install VS Code
echo "Installing VS Code..."
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt-get update
sudo apt-get install -y code

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv /opt/venv
source /opt/venv/bin/activate
pip install --upgrade pip

# Clone the FusionAiAutoCoder repository
echo "Cloning FusionAiAutoCoder repository..."
git clone https://github.com/yourusername/FusionAiAutoCoder.git /home/$USER/FusionAiAutoCoder
cd /home/$USER/FusionAiAutoCoder

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Set up auto-start for development environment (optional)
echo "Setting up auto-start for development environment..."
cat > /home/$USER/.bashrc << 'EOL'
# FusionAiAutoCoder development environment
if [ -f /opt/venv/bin/activate ]; then
    source /opt/venv/bin/activate
fi
EOL

echo "Setup complete! Please log out and back in for all changes to take effect."