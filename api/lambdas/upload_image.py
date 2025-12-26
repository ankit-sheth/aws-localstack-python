"""
Lambda function to upload an image with metadata to S3 and DynamoDB
"""
import json
import base64
import uuid
from datetime import datetime
from config import S3_BUCKET, is_allowed_file, get_content_type

# initialise and get aws clients
from initialize import s3_client, dynamodb, table

def lambda_handler(event, context):
    """
    to upload the image on s2 and save metadata in dynamodb, table
    
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        filename = body.get('filename') ## name of file-image
        image_data = body.get('image_data') ## base64 encoded image data
        metadata = body.get('metadata', {}) ## metadat
        
        # validate, can create helper here or can use some lib
        if not filename or not image_data:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'filename and image_data are required'
                })
            }
        
        if not is_allowed_file(filename):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'file type not allowed. Allowed types: png, jpg, jpeg, gif, bmp, webp'
                })
            }
        
        # -- generate unique image id and s3 key - unique for each image - to reterive back
        image_id = str(uuid.uuid4())
        file_extension = filename.rsplit('.', 1)[1].lower()
        s3_key = f"images/{image_id}.{file_extension}"
        
        # Decode base64 image data
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid base64 image data'
                })
            }
        
        # to upload to s3
        content_type = get_content_type(filename)
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=image_bytes,
            ContentType=content_type
        )
        
        ## for metadata store in dynamodb
        uploaded_at = datetime.utcnow().isoformat() ## currente date time in iso format
        
        item = {
            'image_id': image_id,
            'filename': filename,
            's3_key': s3_key,
            'uploaded_at': uploaded_at,
            'size': len(image_bytes),
            'content_type': content_type,
            'title': metadata.get('title', ''),
            'description': metadata.get('description', ''),
            'tags': metadata.get('tags', [])
        }
        
        table.put_item(Item=item)
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Image uploaded successfully',
                'image_id': image_id,
                'filename': filename,
                's3_key': s3_key,
                'uploaded_at': uploaded_at
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }
