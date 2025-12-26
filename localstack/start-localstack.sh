#!/bin/bash

# Start LocalStack using Docker Compose V2 (compatible with WSL)

echo "Starting LocalStack..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Use Docker Compose V2 (docker compose) instead of docker-compose
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "✅ Using Docker Compose V2"
    docker compose up -d
elif command -v docker-compose &> /dev/null; then
    echo "⚠️  Using legacy docker-compose (may have compatibility issues)"
    docker-compose up -d
else
    echo "❌ Error: Neither 'docker compose' nor 'docker-compose' is available"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ LocalStack started successfully!"
    echo ""
    echo "Waiting for LocalStack to be ready..."
    
    MAX_RETRIES=30
    RETRY_COUNT=0
    until curl -s http://localhost:4566/_localstack/health > /dev/null 2>&1; do
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            echo "❌ LocalStack failed to become ready within the expected time"
            echo "Check logs with: docker logs localstack_image_service_test"
            exit 1
        fi
        echo "Waiting for LocalStack... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done
    
    echo "✅ LocalStack is ready!"
    echo ""
    echo "LocalStack is available at: http://localhost:4566"
    echo ""
    echo "Useful commands:"
    echo "  - View logs: docker logs -f localstack_image_service_test"
    echo "  - Stop: ./stop-localstack.sh or docker compose down"
    echo "  - Health check: curl http://localhost:4566/_localstack/health"
else
    echo "❌ Failed to start LocalStack"
    exit 1
fi
