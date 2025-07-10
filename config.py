import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Pinecone
pinecone_key = os.getenv("pinecone_key")


# Hugging Face or OpenAI
hugging_face = os.getenv("hugging_face")
open_api_key = os.getenv("open_api_key")
