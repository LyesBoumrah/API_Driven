import json
import boto3
import os

INSTANCE_ID = os.environ.get("INSTANCE_ID")

ec2 = boto3.client(
    "ec2",
    endpoint_url="http://localhost.localstack.cloud:4566",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

def lambda_handler(event, context):
    path = event.get("rawPath") or event.get("path", "")

    if path.endswith("/start"):
        ec2.start_instances(InstanceIds=[INSTANCE_ID])
        return {
            "statusCode": 200,
            "body": json.dumps({"action": "start", "instance_id": INSTANCE_ID})
        }

    if path.endswith("/stop"):
        ec2.stop_instances(InstanceIds=[INSTANCE_ID])
        return {
            "statusCode": 200,
            "body": json.dumps({"action": "stop", "instance_id": INSTANCE_ID})
        }

    return {
        "statusCode": 400,
        "body": json.dumps({"error": "Use /start or /stop"})
    }
