.PHONY: help install test clean docker run lint format

help:
	@echo "PII-Shield Engine - Available Commands"
	@echo "======================================="
	@echo "install    : Install package in development mode"
	@echo "test       : Run all tests"
	@echo "test-cov   : Run tests with coverage"
	@echo "test-unit  : Run unit tests only"
	@echo "demo       : Run demo script"
	@echo "docker     : Build Docker image"
	@echo "run        : Start API server"
	@echo "run-dev    : Start API server with auto-reload"
	@echo "lint       : Run code linters"
	@echo "format     : Format code with black"
	@echo "clean      : Remove build artifacts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=pii_shield --cov=api --cov-report=html --cov-report=term

test-unit:
	pytest tests/ -v -m unit

test-integration:
	pytest tests/ -v -m integration

demo:
	python demo.py

docker:
	docker build -t pii-shield-engine:latest .

docker-compose:
	docker-compose up -d

run:
	uvicorn api.main:app --host 0.0.0.0 --port 8000

run-dev:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

lint:
	@echo "Running flake8..."
	flake8 pii_shield/ api/ tests/ || true
	@echo "\nRunning mypy..."
	mypy pii_shield/ api/ || true

format:
	black pii_shield/ api/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/
	@echo "Cleaned build artifacts"
