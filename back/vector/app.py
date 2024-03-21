import json
import os
import tempfile
import boto3

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents.base import Document

s3_client = boto3.client("s3")
vector_bucket = os.environ["VECTOR_BUCKET"]
secret_arn = os.environ["SECRET_ARN"]


def get_secrets() -> dict[str, str]:
    client = boto3.client("secretsmanager")
    resp = client.get_secret_value(SecretId=secret_arn)
    secret_str = resp["SecretString"]
    secrets = json.loads(secret_str)
    return secrets


secrets = get_secrets()
os.environ["OPENAI_API_KEY"] = secrets["OPENAI_API_KEY"]


def lambda_handler(event, context) -> dict:
    print(f"{event=}")
    print(f"{context=}")

    for record in event["Records"]:
        s3 = record["s3"]
        bucket = s3["bucket"]["name"]
        key = s3["object"]["key"]
        handle_object(bucket, key)

    return {"statusCode": 200, "body": json.dumps({"message": "ok"})}


def handle_object(bucket: str, key: str) -> None:
    resp = s3_client.get_object(Bucket=bucket, Key=key)
    doc_bytes = resp["Body"].read()
    raw_docs = load_document(key, doc_bytes)
    docs = split_documents(raw_docs)
    save_vector(docs)


def load_document(key: str, doc_bytes: bytes) -> list[Document]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, key)
        with open(file_path, "wb") as f:
            f.write(doc_bytes)
        loader = PyPDFLoader(file_path)
        raw_docs = loader.load()
        return raw_docs


def split_documents(raw_docs: list[Document]) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )
    docs = text_splitter.split_documents(raw_docs)
    return docs


def save_vector(docs: list[Document]) -> None:
    embeddings = OpenAIEmbeddings()
    with tempfile.TemporaryDirectory() as temp_dir:
        chroma = Chroma.from_documents(
            documents=docs, embedding=embeddings, persist_directory=temp_dir
        )
        result = chroma.similarity_search("Abstract or summary")
        print(f"{result=}")
        file_name = "chroma.sqlite3"
        db_path = os.path.join(temp_dir, file_name)
        upload_object(vector_bucket, file_name, db_path)


def upload_object(bucket: str, key: str, local_path: str) -> None:
    client = boto3.client("s3")
    with open(local_path, "rb") as f:
        client.put_object(Bucket=bucket, Body=f, Key=key)
