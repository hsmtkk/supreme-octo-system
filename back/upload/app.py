import base64
import json
import os
import tempfile
import boto3

source_bucket = os.environ["SOURCE_BUCKET"]

def lambda_handler(event, context) -> dict:
    uploaded = json.loads(event["body"])
    file_name = uploaded["name"]
    doc_bytes_encoded = uploaded["encoded"]
    doc_bytes = base64.b64decode(doc_bytes_encoded)

    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(doc_bytes)
        with open(file_path, "rb") as f:
            client = boto3.client("s3")
            client.put_object(Bucket=source_bucket, Body=f, Key=file_name)

    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}
