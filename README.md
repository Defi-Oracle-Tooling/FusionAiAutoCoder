# FusionAiAutoCoder

FusionAiAutoCoder is an Agentic IDE that leverages AI tools, multi-agent orchestration, and Azure AI Foundry integration to provide automated coding assistance for developers.

## Overview

FusionAiAutoCoder combines the power of multi-agent systems, local processing, and cloud-based AI services to provide an intelligent coding environment. The system can generate code, optimize existing implementations, and help with deployment operations, all through a single unified interface.

Key features include:
- **Multi-Agent Orchestration**: Uses [AutoGen](https://github.com/microsoft/autogen) to create specialized agents for different coding tasks
- **Azure AI Foundry Integration**: Leverages Azure's advanced AI services for improved code generation and optimization
- **Hybrid Processing**: Intelligently routes tasks between local agents and cloud services based on complexity and resource requirements
- **RESTful API**: Provides programmatic access to all functionality via a well-documented API
- **Kubernetes Deployment**: Includes configurations for both development and production environments
- **GPU Acceleration**: Supports GPU acceleration for compute-intensive operations

## Architecture

FusionAiAutoCoder is built with a modular architecture:

```
┌─────────────────┐    ┌──────────────────────┐    ┌────────────────┐
│  Client/User    │───▶│  API Service Layer   │───▶│ Auth/Security  │
└─────────────────┘    └──────────────────────┘    └────────────────┘
                                │
             ┌─────────────────┴────────────────┐
             ▼                                   ▼
┌──────────────────────┐              ┌────────────────────────┐
│   Agent Orchestrator │◀────────────▶│  Azure AI Integration  │
└──────────────────────┘              └────────────────────────┘
      │         │                               │
      │         │                               │
      ▼         ▼                               ▼
┌───────────┐ ┌───────────┐             ┌─────────────────┐
│ Local     │ │ Local     │             │ Azure AI Foundry│
│ Agents    │ │ Processing│             │ Services        │
└───────────┘ └───────────┘             └─────────────────┘
```

## Getting Started

### Prerequisites

- Python 3.8+ 
- Docker (for containerized deployment)
- Kubernetes (for production deployment)
- Azure subscription (for Azure AI Foundry integration)
- OpenAI API key (for AutoGen)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FusionAiAutoCoder.git
   cd FusionAiAutoCoder
   ```

2. Set up the development environment:
   ```bash
   ./scripts/setup_dev_env.sh
   ```

3. Create and configure your `.env` file from the template:
   ```bash
   cp .env.template .env
   # Edit .env with your credentials
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Locally

To run the main application:
```bash
python src/main.py
```

To start the API server:
```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 8080 --reload
```

Alternatively, you can use the provided Makefile commands:
```bash
make run-api
```

### Docker Deployment

Build and run with Docker:
```bash
make build-docker
make run-docker
```

### Kubernetes Deployment

Deploy to a development environment:
```bash
make deploy-dev
```

Deploy to a production environment:
```bash
make deploy-prod
```

## API Documentation

The API documentation is available at `/docs` when the server is running. A comprehensive guide is also available in the [API Documentation](docs/api.md) file.

## Usage Examples

For detailed usage examples, see the [Usage Guide](docs/usage.md).

### Basic Example:

```python
from src.main import hybrid_workflow

# Generate code
result = hybrid_workflow(
    task_type="code_generation",
    task_data={
        "prompt": "Create a function to calculate the factorial of a number",
        "language": "python",
        "complexity": "low"
    }
)

print(result["code"])
```

## Contributing

Contributions are welcome! Please check out our [Contribution Guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [AutoGen](https://github.com/microsoft/autogen) - Multi-agent conversation framework
- Azure AI Services - For advanced AI capabilities