#!/bin/bash
set -e

echo "================================================"
echo "Starting ClaimFlow AI Application"
echo "================================================"

# Function to initialize database
init_database() {
    echo "Initializing database..."
    python scripts/init_database.py
    echo "✅ Database initialized"
}

# Function to ingest policies into vector database
ingest_policies() {
    echo "Ingesting policy documents into ChromaDB..."
    python scripts/ingest_policies.py
    echo "✅ Policies ingested"
}

# Check if database exists
if [ ! -f "/app/data/claimflow.db" ]; then
    echo "Database not found. Creating new database..."
    init_database
else
    echo "✅ Database exists"
fi

# Check if ChromaDB is populated
if [ ! -d "/app/data/chroma_db" ] || [ -z "$(ls -A /app/data/chroma_db)" ]; then
    echo "ChromaDB not populated. Ingesting policies..."
    ingest_policies
else
    echo "✅ ChromaDB populated"
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set!"
    echo "   Set it in .env file or environment variables"
fi

echo "================================================"
echo "Starting application: $1"
echo "================================================"

# Start application based on command
case "$1" in
    gradio)
        echo "Starting Gradio UI..."
        exec python ui/simple_app.py
        ;;
    api)
        echo "Starting FastAPI server..."
        exec python api/main.py
        ;;
    init)
        echo "Running initialization only..."
        init_database
        ingest_policies
        echo "✅ Initialization complete"
        ;;
    test)
        echo "Running tests..."
        exec python -m pytest tests/
        ;;
    shell)
        echo "Starting shell..."
        exec /bin/bash
        ;;
    *)
        echo "Unknown command: $1"
        echo "Available commands: gradio, api, init, test, shell"
        exit 1
        ;;
esac
