
1. to create the local stack and setup execute: (only create local stack - s3,dynamodb,lambda,apigateway,iam,sts)
   ./setup.sh

2. to setup the apis
   cd api
   python3 deploy.py

3. to tets 
   ## go to root
   test_execute_api.py