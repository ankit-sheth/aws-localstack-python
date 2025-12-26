import json
import boto3
from config import AWS_REGION, S3_BUCKET, DYNAMODB_TABLE, ENDPOINT_URL

# initialize the aws clients here
s3_client = boto3.client('s3', region_name=AWS_REGION, endpoint_url=ENDPOINT_URL)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION, endpoint_url=ENDPOINT_URL)
table = dynamodb.Table(DYNAMODB_TABLE)
