.PHONY: install format lint test clean run docker-build docker-run docker-push

# Variables
PYTHON = python
PIP = pip
DOCKER = docker
DOCKER_COMPOSE = docker-compose
PROJECT_NAME = geoscore
DOCKER_IMAGE = $(PROJECT_NAME):latest
DOCKER_USERNAME = yourusername

# Install dependencies
install:
	$(PIP) install -e .[dev]

# Format code
format:
	black .
	isort .

# Lint code
lint:
	flake8 $(PROJECT_NAME) tests
	mypy $(PROJECT_NAME)

# Run tests
test:
	pytest -v --cov=$(PROJECT_NAME) --cov-report=term-missing

# Run the application
run:
	uvicorn $(PROJECT_NAME).main:app --reload

# Clean up build artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/ build/ dist/ *.egg-info/

# Build Docker image
docker-build:
	$(DOCKER) build -t $(DOCKER_IMAGE) .

# Run Docker container
docker-run:
	$(DOCKER) run -p 8000:8000 --env-file .env $(DOCKER_IMAGE)

# Push Docker image to registry
docker-push:
	$(DOCKER) tag $(DOCKER_IMAGE) $(DOCKER_USERNAME)/$(DOCKER_IMAGE)
	$(DOCKER) push $(DOCKER_USERNAME)/$(DOCKER_IMAGE)

# Run with docker-compose
docker-compose-up:
	$(DOCKER_COMPOSE) up --build

# Run tests with coverage in docker
docker-test:
	$(DOCKER_COMPOSE) -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test

# Clean up docker resources
docker-clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans
	$(DOCKER) system prune -f

# Install pre-commit hooks
install-hooks:
	pre-commit install

# Run pre-commit on all files
pre-commit-all:
	pre-commit run --all-files

# Show help
help:
	@echo "Available commands:"
	@echo "  install       - Install the package in development mode"
	@echo "  format        - Format code using black and isort"
	@echo "  lint          - Run linters (flake8 and mypy)"
	@echo "  test          - Run tests with coverage"
	@echo "  run           - Run the application"
	@echo "  clean         - Remove build artifacts"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run Docker container"
	@echo "  docker-push   - Push Docker image to registry"
	@echo "  docker-compose-up - Run with docker-compose"
	@echo "  docker-test   - Run tests in Docker"
	@echo "  docker-clean  - Clean up Docker resources"
	@echo "  install-hooks - Install pre-commit hooks"
	@echo "  pre-commit-all - Run pre-commit on all files"

.DEFAULT_GOAL := help
