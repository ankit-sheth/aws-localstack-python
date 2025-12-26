"""
config file for common configurations 
"""

import os

# aws - (localstack) configuration
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
S3_BUCKET = os.environ.get('S3_BUCKET', 'image-storage-bucket')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'ImageMetadata')
ENDPOINT_URL = os.environ.get('AWS_ENDPOINT_URL', 'http://localhost:4545')

# Image Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def is_allowed_file(filename):
    """
        to check the valid file extension
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_content_type(filename):
    """Get content type based on file extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    content_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',   
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp'
    }
    return content_types.get(ext, 'application/octet-stream')
