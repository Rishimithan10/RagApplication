import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Pinecone
pinecone_key = os.getenv("pinecone_key")


# Hugging Face or OpenAI
hugging_face = os.getenv("hugging_face")
groq_api_key = os.getenv("groq_api_key")

fire_base_api_key=os.getenv("FIREBASE_API_KEY")