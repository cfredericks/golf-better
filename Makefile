.PHONY: help build up down logs test lint migrate clean

# Default target
help:
	@echo "Golf-Better Docker Commands"
	@echo ""
	@echo "Development:"
	@echo "  make up          - Start all services (postgres, backend, web)"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make logs-web    - View web app logs"
	@echo "  make logs-api    - View backend API logs"
	@echo ""
	@echo "Database:"
	@echo "  make migrate     - Run database migrations"
	@echo "  make db-shell    - Open PostgreSQL shell"
	@echo ""
	@echo "Testing:"
	@echo "  make test        - Run all tests"
	@echo "  make test-api    - Run backend tests only"
	@echo "  make test-web    - Run web app tests only"
	@echo ""
	@echo "Linting:"
	@echo "  make lint        - Run all linters"
	@echo "  make lint-api    - Run backend linter (ruff)"
	@echo "  make lint-web    - Run web app linter (eslint)"
	@echo ""
	@echo "Build:"
	@echo "  make build       - Build all Docker images"
	@echo "  make build-web   - Build web app for production"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean       - Remove containers, volumes, and images"

# Development
up:
	docker compose up -d postgres
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 3
	docker compose --profile migrate up migrations
	docker compose up -d backend web
	@echo ""
	@echo "Services started:"
	@echo "  - Web App:  http://localhost:5173"
	@echo "  - Backend:  http://localhost:8080"
	@echo "  - Postgres: localhost:5432"

down:
	docker compose down

logs:
	docker compose logs -f

logs-web:
	docker compose logs -f web

logs-api:
	docker compose logs -f backend

# Database
migrate:
	docker compose --profile migrate up migrations

db-shell:
	docker compose exec postgres psql -U postgres

# Testing
test: test-api test-web

test-api:
	docker compose --profile test run --rm backend-test

test-web:
	docker compose --profile test run --rm web-test

# Linting
lint: lint-api lint-web

lint-api:
	docker compose --profile lint run --rm backend-lint

lint-web:
	docker compose --profile lint run --rm web-lint

# Build
build:
	docker compose build

build-web:
	docker compose --profile build run --rm web-build

# Cleanup
clean:
	docker compose down -v --rmi local
	docker system prune -f
