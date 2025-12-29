"""
Unit tests for get_image Lambda function
"""
import unittest
import json
import base64
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the lambda
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambdas'))

import get_image

class TestGetImage(unittest.TestCase): ## test suite
    
    def setUp(self):
        ## set the fixtures / sample data for unit tetss
        self.sample_metadata = {
            'image_id': 'test-id-123',
            'filename': 'test.jpg',
            's3_key': 'images/test-id-123.jpg',
            'content_type': 'image/jpeg',
            'title': 'Test Image',
            'size': 1024
        }
        
        self.sample_image_data = b'test_image_binary_data'
        
    @patch('get_image.s3_client') ## this will call the mocks3
    @patch('get_image.table') ## this will call the mock table
    def test_successful_get_image(self, mock_table, mock_s3):

        mock_table.get_item.return_value = {
            'Item': self.sample_metadata
        }
        
        ## to mock the s3 response - create dummy response
        mock_s3_response = MagicMock()
        mock_s3_response['Body'].read.return_value = self.sample_image_data
        mock_s3.get_object.return_value = mock_s3_response

        ## create custom event for get_image fnction -actual input for lambda
        ## as there we get image_id as path params, so passing here as pathParameters

        event = {
            'pathParameters': {
                'image_id': 'test-id-123'
            }
        }
        
        response = get_image.lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        # to verify s3 call, @ToDo: not sure this works, need changes may be in key
        mock_s3.get_object.assert_called_once_with(
            Bucket='image-storage-bucket',
            Key='images/test-id-123.jpg'
        )
    
        
    def test_missing_image_id(self):
        ## not passig the image_id as path params, should gives 400 - bad request
        event = {
            'pathParameters': {}
        }
        
        response = get_image.lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 400)
        
        

if __name__ == '__main__':
    unittest.main()
