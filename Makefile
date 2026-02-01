.PHONY: help build up down logs shell test clean rebuild

# Default target
help:
	@echo "ClaimFlow AI - Docker Commands"
	@echo "================================"
	@echo "make build       - Build Docker image"
	@echo "make up          - Start application"
	@echo "make down        - Stop application"
	@echo "make restart     - Restart application"
	@echo "make logs        - View logs"
	@echo "make shell       - Open shell in container"
	@echo "make test        - Run tests in container"
	@echo "make init        - Initialize database and RAG"
	@echo "make clean       - Remove containers and volumes"
	@echo "make rebuild     - Rebuild and restart"
	@echo "make backup      - Backup database and vector store"

# Build Docker image
build:
	docker-compose build

# Start application
up:
	docker-compose up -d
	@echo "✅ Application started"
	@echo "   Gradio UI: http://localhost:7860"

# Stop application
down:
	docker-compose down

# Restart application
restart:
	docker-compose restart

# View logs
logs:
	docker-compose logs -f claimflow-app

# Open shell
shell:
	docker-compose exec claimflow-app /bin/bash

# Run tests
test:
	docker-compose run --rm claimflow-app test

# Initialize database and vector store
init:
	docker-compose run --rm claimflow-app init

# Clean everything
clean:
	docker-compose down -v
	@echo "⚠️  All data deleted!"

# Rebuild and restart
rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "✅ Application rebuilt and restarted"

# Backup data
backup:
	@mkdir -p backup
	docker cp claimflow-ai:/app/data/claimflow.db ./backup/claimflow-$$(date +%Y%m%d-%H%M%S).db
	@echo "✅ Database backed up to backup/"

# View status
status:
	docker-compose ps

# Check health
health:
	docker inspect claimflow-ai --format='{{json .State.Health}}' | python -m json.tool
