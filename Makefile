# Makefile for FusionAiAutoCoder project

.PHONY: help setup test lint format run run-api build-docker run-docker deploy-dev deploy-prod clean-docker

# Default target
.DEFAULT_GOAL := help

# Get Python version
PYTHON := python3
PIP := pip3

# Variables
DOCKER_IMAGE_NAME := fusionaicoder
DOCKER_TAG := latest
DOCKER_FILE := docker-templates/docker-ncads_v4.yml
PORT := 8080

help: ## Show this help
	@echo "FusionAiAutoCoder Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Setup development environment
	$(PIP) install -r requirements.txt

test: ## Run tests
	$(PYTHON) -m pytest -v tests/

lint: ## Run linting checks
	$(PYTHON) -m flake8 src/ tests/

format: ## Format code using black
	$(PYTHON) -m black src/ tests/

run: ## Run the main application
	$(PYTHON) src/main.py

run-api: ## Run the API server
	$(PYTHON) -m uvicorn src.api:app --host 0.0.0.0 --port $(PORT) --reload

build-docker: ## Build Docker image
	docker build -f $(DOCKER_FILE) -t $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) .

run-docker: ## Run Docker container
	docker run -p $(PORT):$(PORT) -e PORT=$(PORT) --name fusionaicoder $(DOCKER_IMAGE_NAME):$(DOCKER_TAG)

run-docker-dev: ## Run Docker container in development mode
	docker run -p $(PORT):$(PORT) -p 8000:8000 -e PORT=$(PORT) --name fusionaicoder-dev $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) dev

clean-docker: ## Remove Docker containers and images
	-docker stop fusionaicoder fusionaicoder-dev
	-docker rm fusionaicoder fusionaicoder-dev
	-docker rmi $(DOCKER_IMAGE_NAME):$(DOCKER_TAG)

deploy-dev: ## Deploy to development environment
	./scripts/aks_setup.sh
	kubectl apply -f kubernetes/dev/

deploy-prod: ## Deploy to production environment
	./scripts/aks_setup.sh
	kubectl apply -f kubernetes/prod/

setup-infra: ## Setup infrastructure using Terraform
	cd terraform && terraform init && terraform apply

terraform-plan: ## Run Terraform plan
	cd terraform && terraform plan -out=tfplan

terraform-apply: ## Apply Terraform plan
	cd terraform && terraform apply tfplan

terraform-destroy: ## Destroy Terraform resources
	cd terraform && terraform destroy

scaffold-project: ## Scaffold a new project
	./scripts/scaffold_project.sh