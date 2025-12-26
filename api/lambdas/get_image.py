"""
Lambda function to view/download an image
"""
import json
import base64
from config import S3_BUCKET

# initialise and get aws clients
from initialize import s3_client, dynamodb, table

def lambda_handler(event, context):
    """
    get the image by image id - single
    
    path param: image_id
    download : true/false , default false 

    """
    try:
        # Get image_id from path parameters
        path_params = event.get('pathParameters', {})
        image_id = path_params.get('image_id')
        
        if not image_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'image_id is required'
                })
            }
        
        # Get metadata from DynamoDB
        response = table.get_item(Key={'image_id': image_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'image not found in dtaa from db'
                })
            }
        
        item = response['Item']
        s3_key = item.get('s3_key')
        content_type = item.get('content_type', 'application/octet-stream')
        filename = item.get('filename', 'image')
        
        # Get image from S3
        s3_response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        image_data = s3_response['Body'].read()
        
        # Check if download parameter is set
        query_params = event.get('queryStringParameters') or {}
        is_download = query_params.get('download', '').lower() == 'true'
        
        # Prepare headers
        headers = {
            'Content-Type': content_type
        }
        
        if is_download:
            headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Return image as base64 encoded (for API Gateway)
        return {
            'statusCode': 200,
            'headers': headers,
            'body': base64.b64encode(image_data).decode('utf-8'), ## image binary data
            'isBase64Encoded': True
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Error: {str(e)}'
            })
        }
