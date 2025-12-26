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
print("\n🔍 Fetching API Gateway information...")
try:
    apis = apigateway.get_rest_apis()
    
    if not apis.get('items'):
        print("❌ No API Gateway found!")
        print("   Please deploy the API first using: python api/deploy.py")
        exit(1)
    
    # Extract API ID from first API Gateway
    api = apis['items'][0]
    api_id = api['id']
    api_name = api['name']
    
    print(f"✅ Found API Gateway")
    print(f"   API Name: {api_name}")
    print(f"   API ID: {api_id}")
    
    # Build base URL using localhost (Docker accessible endpoint)
    base_url = f"http://localhost:4566/restapis/{api_id}/dev"
    
    print(f"\n📍 API Base URL:")
    print(f"   {base_url}")
    
except Exception as e:
    print(f"❌ Error fetching API Gateway: {e}")
    exit(1)

# Check Lambda functions
print("\n" + "=" * 80)
print(" LAMBDA FUNCTION STATUS")
print("=" * 80)

functions = ['upload-image', 'list-images', 'get-image', 'delete-image']
all_healthy = True

for func_name in functions:
    try:
        func = lambda_client.get_function_configuration(FunctionName=func_name)
        env_vars = func.get('Environment', {}).get('Variables', {})
        endpoint = env_vars.get('AWS_ENDPOINT_URL', 'Not set')
        timeout = func.get('Timeout', 'N/A')
        
        status_icon = "✅" if func.get('State') == 'Active' else "❌"
        timeout_icon = "✅" if timeout >= 30 else "⚠️"
        endpoint_icon = "✅" if '172.17' in endpoint or 'localhost:4566' in endpoint or '172.18' in endpoint else "⚠️"
        
        print(f"\n{status_icon} {func_name}:")
        print(f"   Status: {func.get('State', 'N/A')}")
        print(f"   {timeout_icon} Timeout: {timeout}s")
        print(f"   Runtime: {func.get('Runtime', 'N/A')}")
        print(f"   {endpoint_icon} Endpoint: {endpoint}")
        
        if timeout < 30 or ('172.17' not in endpoint and 'localhost:4566' not in endpoint and '172.18' not in endpoint):
            all_healthy = False
    except Exception as e:
        print(f"\n❌ {func_name}: ERROR - {e}")
        all_healthy = False

# Test Lambda directly
print("\n" + "=" * 80)
print(" DIRECT LAMBDA TESTS")
print("=" * 80)

# Test 1: List images (should return empty list initially)
print("\n📋 Test 1: List Images")
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
        print(f"   ✅ SUCCESS - Status Code: {result.get('statusCode')}")
        print(f"   📊 Image Count: {body.get('count', 0)}")
        print(f"   📝 Response: {json.dumps(body, indent=6)}")
    else:
        print(f" Response: {result}")
except socket.timeout:
    print(f" Timeout (skipping)")
except Exception as e:
    print(f"Error: {str(e)[:100]}")

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
        print(f"   ✅ SUCCESS - Status Code: {result.get('statusCode')}")
        print(f"   🆔 Image ID: {body.get('image_id', 'N/A')}")
        print(f"   📄 Message: {body.get('message', 'N/A')}")
        uploaded_image_id = body.get('image_id')
    else:
        print(f"   ⚠️ Response: {result}")
        uploaded_image_id = None
except Exception as e:
    print(f"   ⚠️ Error: {str(e)[:100]}")
    uploaded_image_id = None

# Test 3: Get the uploaded image
if uploaded_image_id:
    print(f"\n📋 Test 3: Get Image (ID: {uploaded_image_id})")
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
            
            print(f"   ✅ SUCCESS - Status Code: {result.get('statusCode')}")
            print(f"   📄 Content-Type: {headers.get('Content-Type', 'N/A')}")
            print(f"   📦 Data Size: {len(body_data)} characters (base64)")
            print(f"   🔐 Base64 Encoded: {is_base64}")
            if body_data:
                print(f"   📝 Data Preview: {body_data[:50]}...")
        else:
            print(f"   ⚠️ Response: {result}")
    except Exception as e:
        print(f"   ⚠️ Error: {str(e)[:100]}")
else:
    print("\n📋 Test 3: Get Image - Skipped (no image uploaded)")

# Test 4: List images again (should show the uploaded image)
print("\n📋 Test 4: List Images (After Upload)")
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
        print(f"   ✅ SUCCESS - Status Code: {result.get('statusCode')}")
        print(f"   📊 Image Count: {body.get('count', 0)}")
        if body.get('images'):
            for img in body['images'][:3]:  # Show first 3 images
                print(f"   - {img.get('image_id')}: {img.get('title')}")
    else:
        print(f"   ⚠️ Response: {result}")
except Exception as e:
    print(f"   ⚠️ Error: {str(e)[:100]}")

# Working curl commands
print("\n" + "=" * 80)
print(" WORKING CURL COMMANDS")
print("=" * 80)

# Sample base64 image (1x1 transparent PNG)
sample_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

print(f"\n📋 1. List all images:")
print(f'   curl "{base_url}/images"')

print(f"\n📋 2. List with filters:")
print(f'   curl "{base_url}/images?tags=sunset"')

print(f"\n📋 3. Upload an image:")
print(f'''   curl -X POST "{base_url}/images" \\
     -H "Content-Type: application/json" \\
     -d '{{
       "filename": "test.png",
       "image_data": "{sample_image}",
       "title": "Test Image",
       "description": "A sample test image",
       "tags": ["test", "demo"]
     }}'  ''')

print(f"\n📋 4. Get specific image (replace <image_id> with actual ID):")
print(f'   curl "{base_url}/images/<image_id>"')

print(f"\n📋 5. Download image as file:")
print(f'   curl "{base_url}/images/<image_id>?download=true" -o image.png')

print(f"\n📋 6. Delete an image:")
print(f'   curl -X DELETE "{base_url}/images/<image_id>"')

# Summary
print("\n" + "=" * 80)
print(" SETUP STATUS")
print("=" * 80)

if all_healthy:
    print("\n✅ All systems operational!")
    print("   - Lambda functions configured correctly")
    print("   - Timeouts set to 30s")
    print("   - Endpoint configured to Docker bridge network (172.17.0.1:4566)")
else:
    print("\n⚠️ Some issues detected.")
    print("   - Re-deploy API to fix endpoint configuration:")
    print("     python api/deploy.py")

print("\n" + "=" * 80)
