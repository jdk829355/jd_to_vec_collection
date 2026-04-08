import logging

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import os


def embed_skill(skill):
    logger = logging.getLogger(__name__)
    client: InferenceClient = InferenceClient(
                    provider="hf-inference",
                    api_key=os.environ["HF_TOKEN"],
            )
    model = os.getenv("HF_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

    embedding = client.feature_extraction(
        model=model,
        text=skill
    )
    logger.info(f"Generated embedding for skill: {skill}")
    return embedding.tolist()

if __name__ == "__main__":
    load_dotenv()
    skill = "Python"
    embedding = embed_skill(skill)
    print(embedding)
