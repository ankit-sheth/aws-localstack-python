#!/usr/bin/env python3
"""
Image Management API - Test and Information Script
This script displays API details, tests Lambda functions, and provides working curl commands.
"""
import boto3
import json
import os

# Set up AWS credentials and endpoint
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Create clients
apigateway = boto3.client('apigateway', endpoint_url='http://localhost:4545')
lambda_client = boto3.client('lambda', endpoint_url='http://localhost:4545')

print("=" * 80)
print(" IMAGE MANAGEMENT API - LocalStack")
print("=" * 80)

# Get API Gateway
apis = apigateway.get_rest_apis()
if apis['items']:
    api = apis['items'][0]
    api_id = api['id']
    api_name = api['name']
    base_url = f"http://localhost:4545/restapis/{api_id}/dev"
    
    print(f"\n✅ API Name: {api_name}")
    print(f"✅ API ID: {api_id}")
    print(f"✅ Base URL: {base_url}")
else:
    print("\n No API Gateway found!")
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
        endpoint_icon = "✅" if '172.18.0.2' in endpoint else "⚠️"
        
        print(f"\n{status_icon} {func_name}:")
        print(f"   Status: {func.get('State', 'N/A')}")
        print(f"   {timeout_icon} Timeout: {timeout}s")
        print(f"   Runtime: {func.get('Runtime', 'N/A')}")
        print(f"   {endpoint_icon} Endpoint: {endpoint}")
        
        if timeout < 30 or '172.18.0.2' not in endpoint:
            all_healthy = False
    except Exception as e:
        print(f"\n❌ {func_name}: ERROR - {e}")
        all_healthy = False

# Test Lambda directly
print("\n" + "=" * 80)
print(" DIRECT LAMBDA TEST")
print("=" * 80)

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
        print(f"\n✅ Direct Lambda Invocation: SUCCESS")
        print(f"   Status Code: {result.get('statusCode')}")
        print(f"   Image Count: {body.get('count', 0)}")
    else:
        print(f"\n⚠️ Direct Lambda Invocation: {result}")
        all_healthy = False
except Exception as e:
    print(f"\n❌ Direct Lambda Test FAILED: {e}")
    all_healthy = False

# Working curl commands
print("\n" + "=" * 80)
print(" WORKING CURL COMMANDS")
print("=" * 80)

# Sample base64 image (1x1 transparent PNG)
sample_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

print(f"\n📋 1. List all images:")
print(f'   curl "{base_url}/images"')

print(f"\n📋 2. List with filters:")
print(f'   curl "{base_url}/images?category=nature&tags=sunset"')

print(f"\n📋 3. Upload an image:")
print(f'''   curl -X POST "{base_url}/images" \\
     -H "Content-Type: application/json" \\
     -d '{{
       "image_data": "{sample_image}",
       "title": "Test Image",
       "description": "A sample test image",
       "tags": ["test", "demo"],
       "category": "testing"
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
    print("   - Endpoint configured to 172.18.0.2:4566")
else:
    print("\n⚠️ Some issues detected. Run fix_timeouts.py and fix_endpoint.py if needed.")

print("\n" + "=" * 80)
