from openai import OpenAI
from config import open_api_key
# Initialize client with your API key
client = OpenAI(api_key=open_api_key)

def generate_answer(chunks, question):
    resume_text = "\n".join(chunks)
    prompt = (
        "You are a helpful AI assistant that reads Documents and answers questions related to the Document.\n\n"
        f"Resume:\n{resume_text}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
