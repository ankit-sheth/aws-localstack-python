#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Management API - Test and Information Script
This script displays API details, tests Lambda functions, and provides working curl commands.
"""
import boto3
import json
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set up AWS credentials and endpoint
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Create clients
apigateway = boto3.client('apigateway', endpoint_url='http://localhost:4566')
lambda_client = boto3.client('lambda', endpoint_url='http://localhost:4566')

print("=" * 80)
print(" IMAGE MANAGEMENT API - LocalStack")
print("=" * 80)

# Step 1: Get API Gateway and extract API ID
print("\ to fetch/get API Gateway information...")
try:
    apis = apigateway.get_rest_apis()
    
    if not apis.get('items'):
        print("no API Gateway found!")
        print("please deploy the API first using: python api/deploy.py")
        exit(1)
    
    # Extract API ID from first API Gateway
    api = apis['items'][0]
    api_id = api['id']
    api_name = api['name']
    
    print(f" fonnd the deployed API Gateway")
    print(f" API Name: {api_name}")
    print(f"API ID: {api_id}")
    
    # Build base URL using localhost (Docker accessible endpoint)
    base_url = f"http://localhost:4566/restapis/{api_id}/dev"
    
    print(f"\n API base URL:")
    print(f"{base_url}")
    
except Exception as e:
    print(f" Error fetching API Gateway: {e}")
    exit(1)

## here, we can check first function status

functions = ['upload-image', 'list-images', 'get-image', 'delete-image']
all_healthy = True


## execute all tets cases

# Test 1: List images (should return empty list initially)
print("\n Test 1: List Images")
try:
    import socket
    socket.setdefaulttimeout(5)
    
    response = lambda_client.invoke(
        FunctionName='list-images',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            'httpMethod': 'GET',
            'path': '/images',
            'queryStringParameters': None,
            'headers': {},
            'body': None
        })
    )
    
    result = json.loads(response['Payload'].read())
    if result.get('statusCode') == 200:
        body = json.loads(result['body'])
        print(f" Status Code: {result.get('statusCode')}")
       
    else:
        print(f" Response: {result}")
except socket.timeout:
    print(f" Timeout (skipping)")
except Exception as e:
    print(f"Error: {str(e)}")

# Test 2: Upload a test image
print("\n Test 2: Upload Image")
sample_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
try:
    response = lambda_client.invoke(
        FunctionName='upload-image',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            'httpMethod': 'POST',
            'path': '/images',
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'filename': 'test-image.png',
                'image_data': sample_image,
                'title': 'Test Image',
                'description': 'A sample test image from test_api.py',
                'tags': ['test', 'demo']
            })
        })
    )
    
    result = json.loads(response['Payload'].read())
    if result.get('statusCode') in [200, 201]:
        body = json.loads(result['body'])
        print(f" Status Code: {result.get('statusCode')}")
        print(f" image id: {body.get('image_id', 'N/A')}")
        uploaded_image_id = body.get('image_id')
    else:
        print(f"   ⚠️ Response: {result}")
        uploaded_image_id = None
except Exception as e:
    print(f" Error: {str(e)}")
    uploaded_image_id = None

# Test 3: Get the uploaded image
if uploaded_image_id:
    print(f"\n Test 3: Get Image (ID: {uploaded_image_id})")
    try:
        response = lambda_client.invoke(
            FunctionName='get-image',
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'httpMethod': 'GET',
                'path': f'/images/{uploaded_image_id}',
                'pathParameters': {'image_id': uploaded_image_id},
                'queryStringParameters': None,
                'headers': {},
                'body': None
            })
        )
        
        payload_data = response['Payload'].read()
        result = json.loads(payload_data)
        
        if result.get('statusCode') == 200:
            # get-image returns the actual image binary data (base64 encoded)
            # not the metadata - it's meant for downloading the image
            headers = result.get('headers', {})
            is_base64 = result.get('isBase64Encoded', False)
            body_data = result.get('body', '')
            
            print(f" Status Code: {result.get('statusCode')}")
            if body_data:
                print(f" image data: {body_data}...")
        else:
            print(f"   response- not 200: {result}")
    except Exception as e:
        print(f" Error: {str(e)}")
else:
    print("\n Test 3: Get Image - Skipped (no image uploaded)")

# Test 4: List images again (should show the uploaded image)
print("\n Test 4: List Images (After Upload)")
try:
    response = lambda_client.invoke(
        FunctionName='list-images',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            'httpMethod': 'GET',
            'path': '/images',
            'queryStringParameters': None,
            'headers': {},
            'body': None
        })
    )
    
    result = json.loads(response['Payload'].read())
    if result.get('statusCode') == 200:
        body = json.loads(result['body'])
        print(f"success - Status Code: {result.get('statusCode')}")
        if body.get('images'):
            for img in body['images'][:3]:  # show only first 3 images
                print(f"   - {img.get('image_id')}: {img.get('title')}")
    else:
        print(f"not 200 - response: {result}")
except Exception as e:
    print(f"Error: {str(e)}")

# Working curl commands
print("###########################################################")
print("###########################################################")
print("###########################################################")

print("working curl commands for Image management API:")

# Sample base64 image (1x1 transparent PNG)
sample_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

print(f"\n 1. List all images:")
print(f'   curl "{base_url}/images"')

print(f"\n 2. List with filters:")
print(f'   curl "{base_url}/images?tags=sunset"')

print(f"\n 3. Upload an image:")
print(f'''   curl -X POST "{base_url}/images" \\
     -H "Content-Type: application/json" \\
     -d '{{
       "filename": "test.png",
       "image_data": "{sample_image}",
       "title": "Test Image",
       "description": "A sample test image",
       "tags": ["test", "demo"]
     }}'  ''')

print(f"\n 4. Get specific image (replace <image_id> with actual ID):")
print(f'   curl "{base_url}/images/<image_id>"')

print(f"\n 5. Download image as file:")
print(f'   curl "{base_url}/images/<image_id>?download=true" -o image.png')

print(f"\n 6. Delete an image:")
print(f'   curl -X DELETE "{base_url}/images/<image_id>"')

# # Summary
# print("\n" + "=" * 80)
# print(" SETUP STATUS")
# print("=" * 80)

# if all_healthy:
#     print("\n✅ All systems operational!")
#     print("   - Lambda functions configured correctly")
#     print("   - Timeouts set to 30s")
#     print("   - Endpoint configured to Docker bridge network (172.17.0.1:4566)")
# else:
#     print("\n⚠️ Some issues detected.")
#     print("   - Re-deploy API to fix endpoint configuration:")
#     print("     python api/deploy.py")

# print("\n" + "=" * 80)
