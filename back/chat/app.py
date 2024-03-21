import boto3
import json
import os
import tempfile

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import OpenAI

vector_bucket = os.environ["VECTOR_BUCKET"]
secret_arn = os.environ["SECRET_ARN"]


def get_secrets() -> dict[str, str]:
    client = boto3.client("secretsmanager")
    resp = client.get_secret_value(SecretId=secret_arn)
    secret_str = resp["SecretString"]
    print(f"{secret_str=}")
    return {"OPENAI_API_KEY": "placeholder"}


secrets = get_secrets()

tmp_dir = tempfile.mkdtemp()


def load_vector(tmp_dir: str) -> None:
    file_name = "chroma.sqlite3"
    file_path = os.path.join(tmp_dir, file_name)
    s3_client = boto3.client("s3")
    resp = s3_client.get_object(Bucket=vector_bucket, Key=file_name)
    content = resp["Body"].read()
    with open(file_path, "wb") as f:
        f.write(content)


load_vector(tmp_dir)


def init_qa_client():
    embeddings = OpenAIEmbeddings()
    chroma = Chroma(persist_directory=tmp_dir, embedding_function=embeddings)
    retriever = chroma.as_retriever()
    qa = RetrievalQA.from_llm(llm=OpenAI(), retriever=retriever)
    return qa


qa_client = init_qa_client()


def lambda_handler(event, context) -> dict:
    print(f"{event=}")
    print(f"{context=}")

    decoded = json.loads(event["body"])
    question = decoded["question"]
    answer = qa_client.invoke(question)
    print(f"{answer=}")

    return {"statusCode": 200, "body": json.dumps(answer)}
