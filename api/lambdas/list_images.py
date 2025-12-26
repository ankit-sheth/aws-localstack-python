"""
Lambda function to list all images with filtering support
"""
import json
from boto3.dynamodb.conditions import Attr

# initialise and get aws clients
from initialize import s3_client, dynamodb, table


def lambda_handler(event, context):
    """
    get all images  (with filters applied if passed any)
    
    optional filters applied as per db (can increase/dcrease as per need):
    - tags: Filter by tags (comma-separated)
    - start_date: Filter by uploaded_at >= start_date (ISO format)
    - end_date: Filter by uploaded_at <= end_date (ISO format)
    - title: Search in title (case-insensitive partial match)
    
    paass as: query params, if date then must pass in this format: 2024-01-01T00:00:00
    """
    try:
        params = event.get('queryStringParameters') or {}
        
        # Scan the table
        scan_kwargs = {}
        filter_expressions = []
        
        
        # to apply filter by staart date
        if params.get('start_date'):
            filter_expressions.append(Attr('uploaded_at').gte(params['start_date']))
        
        ## to apply filter by end date
        if params.get('end_date'):
            filter_expressions.append(Attr('uploaded_at').lte(params['end_date']))
        
        # to apply filter by title - contains
        if params.get('title'):
            filter_expressions.append(Attr('title').contains(params['title']))
        
        # to validate/apply filters - create for db apply
        if filter_expressions:
            filter_expression = filter_expressions[0]
            for expr in filter_expressions[1:]:
                filter_expression = filter_expression & expr
            scan_kwargs['FilterExpression'] = filter_expression
        
        # apply scan to db table
        response = table.scan(**scan_kwargs)
        items = response.get('Items', [])
        
        # pagaination can handle here if needed
        
        # apply sorting
        items.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
        
        # Prepare response (exclude sensitive data)
        images = []
        for item in items:
            images.append({
                'image_id': item.get('image_id'),
                'filename': item.get('filename'),
                'title': item.get('title', ''),
                'description': item.get('description', ''),
                'tags': item.get('tags', []), ## as stored array
                'uploaded_at': item.get('uploaded_at'),
                'size': int(item.get('size', 0)) if item.get('size') else 0,
                'content_type': item.get('content_type'),
                's3_key': item.get('s3_key') ## can remove if not rrequired
            })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'count': len(images),
                'images': images ### list
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Error: {str(e)}'
            })
        }
