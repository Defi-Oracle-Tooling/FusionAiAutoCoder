#!/bin/bash
# filepath: scripts/scaffold_project.sh
# A simple script to scaffold a new project structure

if [ -z "$1" ]; then
  echo "Usage: $0 <project_name>"
  exit 1
fi

PROJECT_NAME=$1

# Add error handling for existing project directory
if [ -d "$PROJECT_NAME" ]; then
  echo "Error: Project '$PROJECT_NAME' already exists."
  exit 1
fi

# Create project directory structure
mkdir -p "$PROJECT_NAME"/{src,tests,docs,scripts,config,data}

# Create initial files
touch "$PROJECT_NAME"/src/main.py "$PROJECT_NAME"/src/utils.py
touch "$PROJECT_NAME"/tests/test_main.py
touch "$PROJECT_NAME"/docs/usage.md
touch "$PROJECT_NAME"/README.md

echo "# $PROJECT_NAME" > "$PROJECT_NAME"/README.md
echo "# Usage instructions" > "$PROJECT_NAME"/docs/usage.md
echo "# .gitignore" > "$PROJECT_NAME"/.gitignore
echo "__pycache__/\n.env\n*.log" >> "$PROJECT_NAME"/.gitignore

# Create a virtual environment
python3 -m venv "$PROJECT_NAME"/venv

# Generate requirements.txt
cat <<EOL > "$PROJECT_NAME"/requirements.txt
pytest
black
flake8
EOL

# Install dependencies in the virtual environment
source "$PROJECT_NAME"/venv/bin/activate
pip install -r "$PROJECT_NAME"/requirements.txt
deactivate

# Add setup script
echo "#!/bin/bash" > "$PROJECT_NAME"/scripts/setup.sh
echo "source ../venv/bin/activate" >> "$PROJECT_NAME"/scripts/setup.sh
chmod +x "$PROJECT_NAME"/scripts/setup.sh

# Add CI/CD pipeline setup instructions
echo "# CI/CD Pipeline Setup" > "$PROJECT_NAME"/docs/cicd.md
echo "Instructions for setting up CI/CD pipelines." >> "$PROJECT_NAME"/docs/cicd.md

# Add placeholder for CI configuration
touch "$PROJECT_NAME"/.github/workflows/ci.yml
echo "# Placeholder for GitHub Actions CI configuration" > "$PROJECT_NAME"/.github/workflows/ci.yml

# Placeholder for AKS setup scripts
# Add commands to set up Azure Kubernetes Service (AKS) with GPU and general compute node pools.

# Add secure connectivity setup
# Placeholder for configuring VNets, NSGs, and VPN/ExpressRoute
# echo "Configuring secure connectivity..."

# Add commands to set up ARM templates or Terraform scripts for resource provisioning
cat <<EOT > arm_templates/main.json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.Compute/virtualMachines",
      "apiVersion": "2021-03-01",
      "name": "DevBox",
      "location": "[resourceGroup().location]",
      "properties": {
        "hardwareProfile": {
          "vmSize": "Standard_DS3_v2"
        }
      }
    }
  ]
}
EOT

# Add instructions to deploy the ARM template
az deployment group create --resource-group myResourceGroup --template-file arm_templates/main.json

# Final message
echo "Project scaffold for '$PROJECT_NAME' created successfully."