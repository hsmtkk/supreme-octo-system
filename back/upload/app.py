import json
import os

def dump_envs() -> None:
    for k,v in os.environ.items():
        print(f"{k=}")
        print(f"{v=}")

def lambda_handler(event, context) -> dict:
    print(f"{event=}")
    print(f"{context=}")
    dump_envs()    
    return {
        "statusCode": 200,
        "body": json.dumps({"message":"ok"})
    }
