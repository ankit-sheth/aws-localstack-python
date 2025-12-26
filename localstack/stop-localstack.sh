#!/bin/bash

# Stop LocalStack using Docker Compose V2

echo "Stopping LocalStack..."

if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose down
elif command -v docker-compose &> /dev/null; then
    docker-compose down
else
    echo " Error: Neither 'docker compose' nor 'docker-compose' is available"
    exit 1
fi

echo " LocalStack stopped"
