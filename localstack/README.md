# LocalStack Setup

# Start LocalStack
cd jsk_self_test_aws/localstack
wsl bash start-localstack.sh

# View logs
wsl docker logs -f localstack_image_service_test

# Check health
curl http://localhost:4566/_localstack/health

# Stop
wsl bash stop-localstack.sh

This folder contains the LocalStack configuration for running AWS services locally.

## Prerequisites

- Docker
- Docker Compose

## Starting LocalStack

```bash
docker-compose up -d
```

## Stopping LocalStack

```bash
docker-compose down
```

## Accessing Services

All AWS services are available at: `http://localhost:4566`

## AWS CLI Configuration

Set the following environment variables:

```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
```

Use the endpoint URL: `http://localhost:4566`

## Services Initialized

- **S3 Bucket**: `image-storage-bucket`
- **DynamoDB Table**: `ImageMetadata`

## Running on WSL (Windows)

### Quick Start (Recommended)

```bash
wsl bash start-localstack.sh
```

### Manual Start

```bash
# Use Docker Compose V2 (without hyphen)
wsl docker compose up -d

# Check status
wsl docker ps --filter "name=localstack"

# View logs
wsl docker logs -f localstack_image_service_test

# Stop
wsl docker compose down
```

### Troubleshooting

**Issue: `KeyError: 'ContainerConfig'`**
- Cause: Legacy `docker-compose` (v1.x) incompatibility
- Solution: Use `docker compose` (V2) instead:
  ```bash
  wsl docker compose up -d  # Not docker-compose
  ```

**Issue: Port already allocated**
- Clean up orphaned containers:
  ```bash
  wsl docker compose down --remove-orphans
  wsl docker system prune -f
  wsl docker compose up -d
  ```

**Issue: Docker not accessible from WSL**
- Enable WSL integration in Docker Desktop settings
- Restart Docker Desktop
