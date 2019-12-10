# netapp-rest-api-demo
Address RESTful endpoint in Python using DynamoDB

This is a microservice which is part of a much larger project, it utilizes DynamoDB as a NoSQL store.

To run the tests locally you need to run dynamodb-local from AWS https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.Docker.html

This application is designed to work with API Gateway/AWS Lambda/AWS Cognito and KMS where IAM roles define access relationships.

Libraries:

boto3
botocore
uuid
pyyaml
json
urllib3
unittest

