.PHONY: help install test lint format type-check clean setup keys docker-build docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

setup: keys ## Set up development environment
	@echo "✓ Development environment ready!"
	@echo "  Run 'make test' to verify installation"

keys: ## Generate encryption keys
	python scripts/genkeys.py

test: ## Run tests
	pytest -v

test-cov: ## Run tests with coverage
	pytest --cov=. --cov-report=html --cov-report=term

lint: ## Run linters
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Format code with black
	black .

format-check: ## Check code formatting
	black --check .

type-check: ## Run type checker
	mypy . --ignore-missing-imports

clean: ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/

docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

