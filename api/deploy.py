#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy Lambda functions and API Gateway to LocalStack
"""
from time import sleep
import boto3
import os
import json
import zipfile
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set up AWS credentials for LocalStack
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
ENV_DEPLOY = os.environ.get('ENV_DEPLOY', 'dev')

ENDPOINT_URL = 'http://localhost:4566'

# create required clients , iam, lambda, apigateway
iam = boto3.client('iam', endpoint_url=ENDPOINT_URL)
lambda_client = boto3.client('lambda', endpoint_url=ENDPOINT_URL)
apigateway = boto3.client('apigateway', endpoint_url=ENDPOINT_URL)

print("=" * 80)
print("deploy images code base to lambda local stack..")
print("=" * 80)

# 1.1: role for iam
print("\n Creating Lambda execution role...")
try:
    role_response = iam.create_role(
        RoleName='lambda-execution-role',
        AssumeRolePolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        })
    )
    print("iam role created")
except iam.exceptions.EntityAlreadyExistsException:
    print("iam role exists, continuing...")

# 2. attach policies to role
print("\n attaching policies to role/iam...")
policies = [
    'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
    'arn:aws:iam::aws:policy/AmazonS3FullAccess',
    'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess'
]

## 1.2 : attach policies to iam
for policy_arn in policies:
    try:
        iam.attach_role_policy(
            RoleName='lambda-execution-role',
            PolicyArn=policy_arn
        )
        print(f" attached {policy_arn.split('/')[-1]}")
    except Exception as e:
        print(f"  Error in Policy attachment: {e}")

# now package lambda functions
print("\n now, package Lambda functions...")
lambdas_dir = Path('lambdas')

## must match with our lambda function files - as codebase function deployed as same name as zip
functions = ['upload_image', 'list_images', 'get_image', 'delete_image']

#  2. combine/put all required files as zip
for func in functions:
    zip_path = lambdas_dir / f"{func}.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(lambdas_dir / f"{func}.py", f"{func}.py")
        zipf.write(lambdas_dir / "config.py", "config.py")
        zipf.write(lambdas_dir / "initialize.py", "initialize.py")
    print(f"  {func}.zip created")

# create lambda functions, using zip files, can use here versions
print("\n creating Lambda functions...")
for func in functions:
    func_name = func.replace('_', '-')
    zip_path = lambdas_dir / f"{func}.zip"
    
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    try:
        lambda_client.create_function(
            FunctionName=func_name,
            Runtime='python3.9',
            Role='arn:aws:iam::000000000000:role/lambda-execution-role',
            Handler=f'{func}.lambda_handler',
            Code={'ZipFile': zip_content},
            Timeout=30,
            Environment={
                'Variables': {
                    'AWS_ENDPOINT_URL': 'http://172.17.0.1:4566'  # Docker bridge network
                }
            }
        )
        print(f"{func_name} created")
    except lambda_client.exceptions.ResourceConflictException:
        print(f"    {func_name} already exists, updating...")
        lambda_client.update_function_code(
            FunctionName=func_name,
            ZipFile=zip_content
        )
        print("wait for code upload, then apply updating configuration...")
        sleep(30)  # need to give some time for the function to be ready

        lambda_client.update_function_configuration(
            FunctionName=func_name,
            Timeout=30,
            Environment={
                'Variables': {
                    'AWS_ENDPOINT_URL': 'http://172.17.0.1:4566'  # Docker bridge network
                }
            }
        )
        print(f"  {func_name} updated")

    
# 3. now create API Gateway
print("\n creating the API Gateway...")
try:
    api_response = apigateway.create_rest_api(
        name='image-management-api',
        description='Image Management API'
    )
    api_id = api_response['id']
    print(f"  API created: {api_id}")
except Exception as e:
    # If API exists, get existing one
    apis = apigateway.get_rest_apis()
    if apis['items']:
        api_id = apis['items'][0]['id']
        print(f"  using existing API: {api_id}")
    else:
        raise e

# get api id - api gateway id
resources = apigateway.get_resources(restApiId=api_id)
root_id = [r['id'] for r in resources['items'] if r['path'] == '/'][0]

## crte /images resource in api gateway - main endpoints
print("1. create image resource")
try:
    images_resource = apigateway.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart='images'
    )
    images_id = images_resource['id']
    print(f"  /images resource created")
except apigateway.exceptions.ConflictException:
    images_id = [r['id'] for r in resources['items'] if r.get('pathPart') == 'images'][0]
    print(f"   /images resource exists")

# get /images/{id} resource
try:
    image_id_resource = apigateway.create_resource(
        restApiId=api_id,
        parentId=images_id,
        pathPart='{id}'
    )
    image_id_id = image_id_resource['id']
    print(f"  /images/{{id}} resource created")
except apigateway.exceptions.ConflictException:
    resources = apigateway.get_resources(restApiId=api_id)
    image_id_id = [r['id'] for r in resources['items'] if r.get('pathPart') == '{id}'][0]
    print(f"   /images/{{id}} resource exists")

# - create the methods in api gateway and integrate with lambda functions
print("\n creating methods and integrations...")

methods_config = [
    ('POST', images_id, 'upload-image'),
    ('GET', images_id, 'list-images'),
    ('GET', image_id_id, 'get-image'),
    ('DELETE', image_id_id, 'delete-image')
]

for http_method, resource_id, function_name in methods_config:
    # create methods in api gateway
    try:
        apigateway.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=http_method,
            authorizationType='NONE'
        )
        print(f"   {http_method} method created")
    except apigateway.exceptions.ConflictException:
        print(f"    {http_method} method exists")
    
    # now integrate function to resource endpoints
    lambda_arn = f'arn:aws:lambda:us-east-1:000000000000:function:{function_name}'
    try:
        apigateway.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=http_method,
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
        )
        print(f"  {http_method} integration created for {function_name}")
    except Exception as e:
        print(f"   Integration: {e}")

# finally, deploy the apis
print("\n finally Deploying API...")
try:
    apigateway.create_deployment(
        restApiId=api_id,
        stageName=ENV_DEPLOY
    )
    print(f"apis deployed to '{ENV_DEPLOY}' stage")
except Exception as e:
    print(f"error in deployment: {e}")

# Print summary
print("\n" + "=" * 80)
print("Deployment complete!")
print("=" * 80)
print(f"\nAPI Base URL: http://localhost:4566/restapis/{api_id}/dev")
print(f"\nEndpoints:")
print(f"  POST   /images           - Upload image")
print(f"  GET    /images           - List images")
print(f"  GET    /images/{{id}}      - View/download image")
print(f"  DELETE /images/{{id}}      - Delete image")
print("\n" + "=" * 80)
