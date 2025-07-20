from openai import OpenAI
from config import open_api_key
# Initialize client with your API key
client = OpenAI(api_key=open_api_key)

def generate_answer(chunks, question):
    doc_text = "\n".join(chunks)
    prompt = (
        "You are a helpful AI assistant that reads Documents and answers questions related to the Document.And alway use the word document not resume\n"
        f"Document:\n{doc_text}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
