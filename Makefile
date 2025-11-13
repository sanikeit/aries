# Aries-Edge Platform Makefile

.PHONY: help build build-all build-api build-frontend build-processor test test-all lint lint-all clean clean-all dev dev-api dev-frontend dev-processor docker-build docker-up docker-down install-deps

# Default target
help:
	@echo "Aries-Edge Platform Build System"
	@echo "================================="
	@echo ""
	@echo "Available targets:"
	@echo "  build          - Build all services"
	@echo "  build-api      - Build API service"
	@echo "  build-frontend - Build frontend service"
	@echo "  build-processor- Build processor service"
	@echo "  test           - Run all tests"
	@echo "  test-all       - Run all tests with coverage"
	@echo "  lint           - Lint all code"
	@echo "  lint-all       - Lint all code with auto-fix"
	@echo "  clean          - Clean build artifacts"
	@echo "  clean-all      - Clean all build artifacts"
	@echo "  dev            - Start development environment"
	@echo "  dev-api        - Start API service in development"
	@echo "  dev-frontend   - Start frontend service in development"
	@echo "  dev-processor  - Start processor service in development"
	@echo "  docker-build   - Build Docker images"
	@echo "  docker-up      - Start Docker services"
	@echo "  docker-down    - Stop Docker services"
	@echo "  install-deps   - Install all dependencies"

# Build targets
build: build-all

build-all: build-api build-frontend build-processor

build-api:
	@echo "Building API service..."
	cd services/api && docker build -t aries-api:latest .

build-frontend:
	@echo "Building frontend service..."
	cd services/frontend && npm run build

build-processor:
	@echo "Building processor service..."
	cd services/processor && docker build -t aries-processor:latest .

# Test targets
test: test-all

test-all:
	@echo "Running all tests..."
	cd services/api && pytest tests/ -v
	cd services/frontend && npm test
	cd services/processor && echo "Processor tests: TBD"

# Lint targets
lint: lint-all

lint-all:
	@echo "Linting all code..."
	cd services/api && black app/ && isort app/ && flake8 app/
	cd services/frontend && npm run lint
	cd services/processor && black *.py && isort *.py && flake8 *.py

# Clean targets
clean: clean-all

clean-all:
	@echo "Cleaning build artifacts..."
	rm -rf services/frontend/dist
	rm -rf services/frontend/node_modules/.cache
	rm -rf packages/schemas/dist
	rm -rf packages/schemas/node_modules/.cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Development targets
dev: dev-all

dev-all: install-deps
	@echo "Starting development environment..."
	docker-compose up -d aries-db aries-broker
	@echo "Database and broker started. Run 'make dev-api', 'make dev-frontend', 'make dev-processor' to start services."

dev-api:
	@echo "Starting API service..."
	cd services/api && python -m app.main

dev-frontend:
	@echo "Starting frontend service..."
	cd services/frontend && npm run dev

dev-processor:
	@echo "Starting processor service..."
	cd services/processor && python main_processor.py

# Docker targets
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

# Dependency installation
install-deps:
	@echo "Installing dependencies..."
	npm install
	cd services/frontend && npm install
	cd services/api && pip install -r requirements.txt
	cd services/processor && pip install -r requirements.txt
	cd packages/schemas && npm install

# Advanced targets
build-schemas:
	@echo "Building shared schemas..."
	cd packages/schemas && npm run build

type-check:
	@echo "Running TypeScript type checking..."
	cd services/frontend && npm run type-check

format:
	@echo "Formatting code..."
	cd services/api && black app/
	cd services/frontend && npm run format
	cd services/processor && black *.py

# CI/CD targets
ci-build:
	@echo "CI build process..."
	make lint
	make test
	make build

ci-deploy:
	@echo "CI deployment process..."
	make docker-build
	make docker-up