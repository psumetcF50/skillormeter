"""
A module to handle the Amazon Bedrock models
"""


import boto3
from langchain_aws import ChatBedrockConverse

def get_llm_model() -> ChatBedrockConverse:
    session = boto3.Session(profile_name="smoke", region_name="us-west-2")
    client = session.client("bedrock-runtime")
    model_name = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    model = ChatBedrockConverse(
                model=model_name,
                client=client,
                temperature=0.0
            )
    return model

