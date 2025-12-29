
1. to create the local stack and setup execute: (only create local stack - s3,dynamodb,lambda,apigateway,iam,sts)

** prerequisite : docker

   ./setup.sh

2. to setup the apis
   cd api
   python3 deploy.py

3. to test
   go to root
  *python3 test_api_execute.py