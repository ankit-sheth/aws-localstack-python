"""
Lambda function to delete an image
"""
import json
from config import S3_BUCKET

# initialise and get aws clients
from initialize import s3_client, dynamodb, table
# s3_client = boto3.client('s3', region_name=AWS_REGION, endpoint_url=ENDPOINT_URL)
# dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION, endpoint_url=ENDPOINT_URL)
# table = dynamodb.Table(DYNAMODB_TABLE)

def lambda_handler(event, context):
    """
    delete the image by image_id
    
    path param: image_id

    1. find the image from db
    2. delte from s3
    3. delete from dynamo db 

    """
    try:
        # first get the image_id from path parameters
        path_params = event.get('pathParameters', {})
        image_id = path_params.get('image_id')
        
        if not image_id:
            return {
                'statusCode': 400,  ##bad request
                'body': json.dumps({
                    'error': 'image id is required'
                })
            }
        
        # get form dyanmocdb
        try:
            response = table.get_item(Key={'image_id': image_id})
        except Exception as db_error:
            print(f" getting iterm error in deltee process: {str(db_error)}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Error: to get item from db'
                })
            }
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'image not found in response- db'
                })
            }
        
        item = response['Item']
        s3_key = item.get('s3_key') ## s3 user key for that image
        
        # actually delete form s3
        try:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
        except Exception as s3_error:
            print(f"S3 deletion error: {str(s3_error)}")
        
        # now delete from dynamodb
        table.delete_item(Key={'image_id': image_id})
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'image has been deleted successfully',
                'image_id': image_id
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'error in getting data: {str(e)}'
            })
        }
