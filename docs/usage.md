# FusionAiAutoCoder Usage Guide

## Overview

FusionAiAutoCoder is an AI-powered tool for automating code generation, optimization, and deployment using a hybrid approach combining local execution and cloud AI services. This guide covers how to use FusionAiAutoCoder effectively.

## Installation

### Prerequisites

- Python 3.9+
- Docker (for containerized deployment)
- Azure account (for Azure AI Foundry integration)
- GPU support (optional but recommended)

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/FusionAiAutoCoder.git
cd FusionAiAutoCoder
```

2. **Install dependencies**

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the project root with the following variables:

```
# Azure Configuration
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_FOUNDRY_ENDPOINT=https://api.foundry.azure.com

# API Configuration
API_KEY=your-secret-api-key
PORT=8080

# Logging
LOG_LEVEL=INFO
```

## Basic Usage

### Starting the API Server

```bash
python -m src.api
```

This will start the API server on the port specified in your `.env` file (default: 8080).

### Using the Python Library

You can also use FusionAiAutoCoder as a Python library in your own code:

```python
from src.main import hybrid_workflow

# Generate code
result = hybrid_workflow(
    task_type="code_generation",
    task_data={
        "prompt": "Create a function to validate email addresses",
        "language": "python",
        "complexity": "low"
    }
)

print(result.get('code', 'No code generated'))

# Optimize code
result = hybrid_workflow(
    task_type="code_optimization",
    task_data={
        "code": "def factorial(n):\n    if n == 0: return 1\n    return n * factorial(n-1)",
        "optimization_target": "performance",
        "language": "python"
    }
)

print(result.get('optimized_code', 'No optimization performed'))
```

### Batch Processing

For processing multiple tasks at once:

```python
from src.main import batch_process

tasks = [
    {
        "task_type": "code_generation",
        "task_data": {
            "prompt": "Create a function to find prime numbers",
            "language": "python"
        }
    },
    {
        "task_type": "code_optimization",
        "task_data": {
            "code": "def factorial(n):\n    if n == 0: return 1\n    return n * factorial(n-1)",
            "optimization_target": "performance"
        }
    }
]

results = batch_process(tasks)
for result in results:
    print(result)
```

## API Usage

See the [API Documentation](api.md) for detailed information on using the REST API.

### Example API Requests

#### Code Generation

```bash
curl -X POST "http://localhost:8080/api/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "prompt": "Create a function to validate email addresses",
    "language": "python",
    "complexity": "low",
    "use_gpu": false
  }'
```

#### Code Optimization

```bash
curl -X POST "http://localhost:8080/api/optimize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "code": "def factorial(n):\n    if n == 0: return 1\n    return n * factorial(n-1)",
    "optimization_target": "performance",
    "language": "python"
  }'
```

## Docker Deployment

To deploy FusionAiAutoCoder using Docker:

```bash
# Build the Docker image
docker build -t fusion-ai-autocoder -f docker-templates/Dockerfile .

# Run the container
docker run -p 8080:8080 --env-file .env fusion-ai-autocoder
```

For GPU support:

```bash
docker run -p 8080:8080 --gpus all --env-file .env fusion-ai-autocoder
```

## Kubernetes Deployment

FusionAiAutoCoder includes Kubernetes configuration for both development and production environments:

```bash
# Development deployment
kubectl apply -f kubernetes/dev/deployment.yaml

# Production deployment
kubectl apply -f kubernetes/prod/deployment.yaml
```

## Troubleshooting

### Common Issues

1. **Azure Authentication Errors**:
   - Verify your Azure credentials in the `.env` file
   - Check that your Azure account has access to AI Foundry services

2. **GPU Not Detected**:
   - Run `python -c "import torch; print(torch.cuda.is_available())"` to verify GPU availability
   - Ensure you have the correct CUDA drivers installed

3. **API Connection Issues**:
   - Check that the API server is running (`ps aux | grep api.py`)
   - Verify the correct port is being used and not blocked by a firewall

### Logs

Logs are stored in the `logs` directory by default. You can change the log level in the `.env` file.

## Advanced Configuration

For advanced configuration options, edit the configuration files in the `src/config` directory:

- `config_multi_agents.py`: Configure the multi-agent orchestration system
- Custom environment variables in `.env`

## Support and Feedback

For support or to provide feedback, please open an issue on the GitHub repository or contact the project maintainers.

## CLI Usage Examples

### Generate Code
```bash
python src/cli.py generate "Create a function to validate email addresses" --language python
```

### Optimize Code
```bash
python src/cli.py optimize /path/to/code.py --target performance
```

### Deploy Infrastructure
```bash
git push origin main
# The deploy.yml workflow will automatically provision infrastructure and deploy the application.
```