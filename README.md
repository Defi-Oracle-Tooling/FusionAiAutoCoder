# FusionAiAutoCoder

## Overview
FusionAiAutoCoder is a next-generation Agentic IDE designed to super-scale code development through fully automated, multi-agent processes. It integrates advanced AI tools, multi-agent orchestration, and dynamic prompt engineering to revolutionize software development.

## Features
- Automated project scaffolding.
- Multi-agent orchestration for code generation, testing, and deployment.
- Integration with CI/CD pipelines.

## Usage
1. Run the scaffold script to create a new project:
   ```bash
   ./scripts/scaffold_project.sh <project_name>
   ```
2. Navigate to the project directory and activate the virtual environment:
   ```bash
   cd <project_name>
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run tests:
   ```bash
   pytest tests/
   ```

## CI/CD Setup
1. Navigate to the `.github/workflows/` directory.
2. Edit the `ci.yml` file to define your CI/CD pipeline.
3. Push changes to your repository to trigger the pipeline.

## Team Enablement

### Training
- Conduct training sessions for team members on Azure AI Foundry and AKS.

### Feedback
- Establish feedback loops using retrospectives and surveys.

## Architecture and Process Flow

### Refined Requirements
- Validated with stakeholders as of March 30, 2025.

### Updated Architectural Diagrams
- Diagrams and process flows have been updated to reflect the current blueprint.

For more details, refer to the `docs/usage.md` file.

## VM/VMSS Setup Instructions

1. **Choose Your VM/VMSS**
   - For single instances, create a VM with sufficient CPU/GPU resources using your preferred cloud provider.
   - For scaling, use Azure VM Scale Sets (VMSS).

2. **VS Code Insiders & AI Toolkit**
   - Install [VS Code Insiders](https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode) on your VM.
   - From the Extensions Marketplace, install the **AI Toolkit** plugin to simplify generative AI development.

3. **ONNX / Ollama Setup**
   - Convert AI models to [ONNX](https://onnx.ai/) format and install ONNX Runtime.
   - Or, for larger language models, install and configure [Ollama](https://ollama.ai/) ensuring sufficient VM resources.

4. **AutoGen Integration**
   - Install and configure [AutoGen](https://github.com/microsoft/autogen) to orchestrate multiple AI agents.
   - Use AutoGen Studio for a low-code prototyping interface.

5. **Enable Multiple AI Agents**
   - Integrate Azure AI Agent Service or [Semantic Kernel](https://github.com/microsoft/semantic-kernel) to manage diverse tasks.

6. **Optimization & Additional Tools**
   - Enable GPU acceleration.
   - Use Docker containers to manage dependencies.
   - Set up monitoring tools (e.g., Application Insights) for performance tracking.