import base64
import json
import os
import tempfile
import boto3

source_bucket = os.environ["SOURCE_BUCKET"]

def lambda_handler(event, context) -> dict:
    print(f"{event=}")
    print(f"{context=}")

    doc_bytes_encoded = event["body"]
    doc_bytes = base64.b64decode(doc_bytes_encoded)

    with tempfile.NamedTemporaryFile(delete_on_close=False) as temp_file:
        temp_file.write(doc_bytes)
        temp_file.close()
        upload_object(source_bucket, "doc.pdf", temp_file.name)

    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}

def upload_object(bucket: str, key: str, local_path: str) -> None:
    client = boto3.client("s3")
    with open(local_path, "rb") as f:
        client.put_object(Bucket=bucket, body=f, Key=key)
