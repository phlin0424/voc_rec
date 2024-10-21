from config import settings
from abc import ABC, abstractmethod

import boto3
from fastapi import HTTPException
from openai import OpenAI
import json


class EmbeddingBase(ABC):
    def __init__(self):
        self.create_client()

    @abstractmethod
    def create_client(self) -> None:
        """Create a client to access to embedding API endpoint"""
        pass

    @abstractmethod
    def create_vector(self, input: str, model_name: str) -> list[int]:
        pass


class OpenAIEmbedding(EmbeddingBase):
    def create_client(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)

    def create_vector(
        self,
        input: str,
        model_name: str = "text-embedding-3-small",
    ) -> list[int]:
        response = self.client.embeddings.create(input=[input], model=model_name)
        return response.data[0].embedding


class BedrockEmbedding(EmbeddingBase):
    def create_client(self) -> None:
        self.client = boto3.client("bedrock-runtime")

    def create_vector(
        self,
        input: str,
        model_name: str = "amazon.titan-embed-text-v1",
    ) -> list[int]:
        bedrock_body = {"inputText": input}
        body_bytes = json.dumps(bedrock_body).encode("utf-8")
        response = self.client.invoke_model(
            accept="*/*",
            body=body_bytes,
            contentType="application/json",
            modelId=model_name,
        )
        response_body = json.loads(response.get("body").read())

        # print(response_body.get("inputTextTokenCount"))
        embedding = response_body.get("embedding")
        return embedding


def generate_vector(text: str, embedding: str = "OpenAI") -> list:
    try:
        if embedding == "OpenAI":
            embedding_generator = OpenAIEmbedding()
        elif embedding == "Bedrock":
            embedding_generator = BedrockEmbedding()
        else:
            raise RuntimeError(
                f"The specified an embedding service is not available {embedding}"
            )
        return embedding_generator.create_vector(input=text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding API error: {e}")


if __name__ == "__main__":
    # The default embedding method:
    print(len(generate_vector("세븐틴")))
    # 1536

    # Other services:
    print(len(generate_vector("세븐틴", embedding="Bedrock")))
    # 1536
