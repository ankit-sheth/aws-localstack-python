# LocalStack on WSL - Setup Complete! ✅

## Summary

Successfully resolved LocalStack compatibility issues on WSL. The main problems were:

1. **Docker Compose V1 incompatibility** (`KeyError: 'ContainerConfig'`)
   - Solution: Use `docker compose` (V2) instead of legacy `docker-compose`
   
2. **Port 4545 conflicts**
   - Solution: Switched to standard LocalStack port 4566

## Current Status

✅ LocalStack is running on `http://localhost:4566`
✅ Services available: S3, DynamoDB, Lambda, API Gateway, IAM, STS

## Quick Start Commands

### From Windows PowerShell

```powershell
# Start LocalStack
cd jsk_self_test_aws/localstack
wsl bash start-localstack.sh

# Check status
wsl docker ps --filter "name=localstack"

# View logs
wsl docker logs -f localstack_image_service_test

# Stop LocalStack
wsl bash stop-localstack.sh
# OR
wsl docker compose down
```

### From WSL Terminal

```bash
cd /mnt/c/Users/asheth/projects/test/jsk_self_test_aws/localstack

# Start
./start-localstack.sh
# OR
docker compose up -d

# Stop
./stop-localstack.sh
# OR
docker compose down
```

## Verify Services

```bash
# Health check
curl http://localhost:4566/_localstack/health

# List S3 buckets (after initialization)
aws --endpoint-url=http://localhost:4566 s3 ls

# List DynamoDB tables (after initialization)
aws --endpoint-url=http://localhost:4566 dynamodb list-tables
```

## Key Changes Made

1. **Updated `docker-compose.yml`**: 
   - Changed port mapping from `4545:4566` to `4566:4566`
   - Added `restart: unless-stopped` policy

2. **Created helper scripts**:
   - `start-localstack.sh` - Smart startup with health checks
   - `stop-localstack.sh` - Clean shutdown

3. **Updated documentation**:
   - `README.md` - Added WSL troubleshooting section
   - All ports updated from 4545 to 4566

## Important Notes

- **Always use `docker compose`** (V2), not `docker-compose` (V1)
- LocalStack runs inside WSL using Docker Desktop's WSL integration
- Port 4566 is the standard LocalStack gateway port
- Init script `init-aws.sh` automatically creates S3 bucket and DynamoDB table

## Next Steps

1. Run the complete setup:
   ```bash
   cd jsk_self_test_aws
   wsl bash setup.sh
   ```

2. Test the API endpoints (commands shown at end of setup.sh)

## Troubleshooting

If you encounter issues:

```bash
# Clean restart
wsl docker compose down --remove-orphans
wsl docker system prune -f
wsl docker compose up -d

# Check Docker Desktop WSL integration
# Settings → Resources → WSL Integration → Enable for your distro
```
