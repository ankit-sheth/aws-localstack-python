#!/bin/bash

echo "Initializing LocalStack AWS resources..."

# Set AWS endpoint and region
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
ENDPOINT_URL=http://localhost:4566

# Create S3 bucket for images
echo "Creating S3 bucket..."
awslocal s3 mb s3://image-storage-bucket

# Create DynamoDB table for image metadata
echo "Creating DynamoDB table..."
awslocal dynamodb create-table \
    --table-name ImageMetadata \
    --attribute-definitions \
        AttributeName=image_id,AttributeType=S \
        AttributeName=uploaded_at,AttributeType=S \
    --key-schema \
        AttributeName=image_id,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"uploaded_at-index\",
                \"KeySchema\": [{\"AttributeName\":\"uploaded_at\",\"KeyType\":\"HASH\"}],
                \"Projection\":{\"ProjectionType\":\"ALL\"},
                \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
            }
        ]"

echo "LocalStack initialization complete!"
