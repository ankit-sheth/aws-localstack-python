#!/bin/bash

# Quick start script to set up the entire project

echo "=== Image Management API - Quick Start ==="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo " Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

echo " Docker is running"

# Start LocalStack
echo ""
echo "Starting LocalStack..."
cd localstack
docker-compose up -d

echo "Waiting for LocalStack to be ready..."
sleep 10

# Check if LocalStack is ready
MAX_RETRIES=30
RETRY_COUNT=0
until curl -s http://localhost:4566/_localstack/health > /dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo " LocalStack failed to start within the expected time"
        exit 1
    fi
    echo "Waiting for LocalStack... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

echo "✅ LocalStack is ready"

# Deploy API
echo ""
echo "Deploying API..."
cd ../api
bash deploy.sh

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To test the API, use the endpoints shown above."
echo ""
echo "Quick test commands:"
echo "  1. Upload an image:"
echo "     BASE64_IMAGE=\$(base64 -w 0 your_image.jpg)"
echo "     curl -X POST http://localhost:4566/restapis/\$API_ID/prod/_user_request_/images \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"filename\": \"test.jpg\", \"image_data\": \"'\$BASE64_IMAGE'\"}'"
echo ""
echo "  2. List images:"
echo "     curl http://localhost:4566/restapis/\$API_ID/prod/_user_request_/images"
echo ""
echo "To stop LocalStack:"
echo "  cd localstack && docker-compose down"
echo ""
