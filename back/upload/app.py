import base64
import json
import os
import tempfile
import boto3

source_bucket = os.environ["SOURCE_BUCKET"]

def lambda_handler(event, context) -> dict:
    uploaded = json.loads(event["body"])
    file_name = uploaded["name"]
    doc_bytes_encoded:str = uploaded["encoded"]
    doc_bytes = base64.b64decode(doc_bytes_encoded)

    client = boto3.client("s3")
    client.put_object(Bucket=source_bucket, Body=doc_bytes, Key=file_name)
    client.put_object(Bucket=source_bucket, Body=doc_bytes_encoded.encode(), Key=file_name + ".txt")

    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}
