# Docker Deployment Guide

This guide explains how to run ClaimFlow AI using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM recommended
- OpenAI API key

## Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd claimflow-ai
```

### 2. Set Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Build and Run with Docker Compose
```bash
# Build and start the application
docker-compose up -d

# Check logs
docker-compose logs -f claimflow-app

# Access application
# Gradio UI: http://localhost:7860
```

### 4. Stop Application
```bash
docker-compose down

# To remove volumes (database, vector store)
docker-compose down -v
```

## Docker Commands

### Build Image
```bash
# Build the Docker image
docker build -t claimflow-ai:latest .

# Build with no cache
docker build --no-cache -t claimflow-ai:latest .
```

### Run Container Manually
```bash
# Run with Gradio UI
docker run -d \
  --name claimflow \
  -p 7860:7860 \
  -e OPENAI_API_KEY=sk-your-key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  claimflow-ai:latest

# Run with shell access
docker run -it \
  --name claimflow-debug \
  -p 7860:7860 \
  -e OPENAI_API_KEY=sk-your-key \
  -v $(pwd)/data:/app/data \
  claimflow-ai:latest shell
```

### Manage Containers
```bash
# View running containers
docker ps

# View logs
docker logs -f claimflow

# Stop container
docker stop claimflow

# Remove container
docker rm claimflow

# Enter running container
docker exec -it claimflow /bin/bash
```

## Docker Compose Commands

### Basic Operations
```bash
# Start services
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose stop

# Remove services and volumes
docker-compose down -v
```

### Individual Service Management
```bash
# Start specific service
docker-compose up -d claimflow-app

# View service logs
docker-compose logs -f claimflow-app

# Restart service
docker-compose restart claimflow-app

# Execute command in service
docker-compose exec claimflow-app python scripts/test_rag.py
```

### Rebuild After Code Changes
```bash
# Rebuild and restart
docker-compose up -d --build

# Force rebuild
docker-compose build --no-cache
docker-compose up -d
```

## Container Commands

The entrypoint script supports multiple commands:

### Gradio UI (Default)
```bash
docker-compose run claimflow-app gradio
```

### FastAPI Backend
```bash
docker-compose run -p 8000:8000 claimflow-app api
```

### Initialize Database Only
```bash
docker-compose run claimflow-app init
```

### Run Tests
```bash
docker-compose run claimflow-app test
```

### Interactive Shell
```bash
docker-compose run claimflow-app shell
```

## Volume Management

### Data Persistence
The following directories are mounted as volumes:

- `./data` → `/app/data` - SQLite database, policies
- `./data/chroma_db` → `/app/data/chroma_db` - Vector database
- `./logs` → `/app/logs` - Application logs

### Backup Data
```bash
# Backup database
docker cp claimflow:/app/data/claimflow.db ./backup/claimflow-$(date +%Y%m%d).db

# Backup vector database
docker cp claimflow:/app/data/chroma_db ./backup/chroma_db-$(date +%Y%m%d)
```

### Restore Data
```bash
# Restore database
docker cp ./backup/claimflow-20260201.db claimflow:/app/data/claimflow.db

# Restart to reload
docker-compose restart claimflow-app
```

## Environment Variables

Configure via `.env` file or docker-compose environment section:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `MODEL_NAME` | LLM model | gpt-4o |
| `TEMPERATURE` | Model temperature | 0.7 |
| `DATABASE_URL` | SQLite database path | sqlite:///data/claimflow.db |
| `LOG_LEVEL` | Logging level | INFO |
| `GRADIO_SERVER_PORT` | Gradio port | 7860 |
| `CHROMA_DB_PATH` | Vector DB path | data/chroma_db |

## Networking

### Port Mapping
- **7860** - Gradio web interface
- **8000** - FastAPI backend (if enabled)

### Custom Network
Services communicate via `claimflow-network` bridge network.

### Expose to Internet
```bash
# Using ngrok (for demo/testing)
ngrok http 7860

# Or set in .env
GRADIO_SHARE=true
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs claimflow-app

# Check if port is in use
netstat -an | grep 7860

# Try different port
docker-compose down
# Edit docker-compose.yml: "8080:7860"
docker-compose up -d
```

### Database Issues
```bash
# Reinitialize database
docker-compose exec claimflow-app python scripts/init_database.py --reset --seed

# Check database
docker-compose exec claimflow-app sqlite3 /app/data/claimflow.db ".tables"
```

### Vector Database Issues
```bash
# Reingest policies
docker-compose exec claimflow-app python scripts/ingest_policies.py

# Check ChromaDB
docker-compose exec claimflow-app python -c "from agent.rag import VectorStore; print(VectorStore().get_document_count())"
```

### Memory Issues
```bash
# Check container resources
docker stats claimflow

# Increase memory limit in docker-compose.yml
services:
  claimflow-app:
    deploy:
      resources:
        limits:
          memory: 4G
```

### Permission Issues
```bash
# Fix permissions on host
chmod -R 755 data/
chmod -R 755 logs/

# Or run as specific user
docker-compose exec -u root claimflow-app chown -R appuser:appuser /app/data
```

## Production Considerations

### Security
```bash
# Don't commit .env
echo ".env" >> .gitignore

# Use secrets management
docker-compose.yml:
  secrets:
    - openai_api_key
```

### Performance
```bash
# Use mounted volumes for better I/O
# Enable Docker BuildKit
export DOCKER_BUILDKIT=1

# Multi-stage builds (already implemented)
```

### Monitoring
```bash
# Add health checks
docker inspect claimflow --format='{{json .State.Health}}'

# View resource usage
docker stats claimflow
```

### Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Multi-Container Setup

For production, you might want separate containers:

```yaml
services:
  claimflow-ui:
    build: .
    command: gradio
    ports: ["7860:7860"]
  
  claimflow-api:
    build: .
    command: api
    ports: ["8000:8000"]
  
  nginx:
    image: nginx:alpine
    ports: ["80:80"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

## CI/CD Integration

### Build in CI
```yaml
# .github/workflows/docker.yml
- name: Build Docker image
  run: docker build -t claimflow-ai:${{ github.sha }} .

- name: Push to registry
  run: docker push claimflow-ai:${{ github.sha }}
```

### Deploy
```bash
# On server
docker pull claimflow-ai:latest
docker-compose up -d --no-deps --build claimflow-app
```

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Inspect container: `docker exec -it claimflow /bin/bash`
- Review environment: `docker-compose config`
