from config import settings
from fastapi import HTTPException
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)


def generate_vector(text: str) -> list:
    try:
        response = client.embeddings.create(
            input=[text],
            model="text-embedding-3-small",  # Choose an appropriate model
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")


if __name__ == "__main__":
    print(generate_vector("세븐틴"))
