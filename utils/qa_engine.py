from groq import Groq
from utils import latency
from config import groq_api_key

client = Groq(api_key=groq_api_key)

def generate_answer(chunks, question):
    doc_text = "\n".join(chunks)
    prompt = (
        "You are a helpful AI assistant that reads Documents and answers questions related to the Document. And always use the word document not resume\n"
        f"Document:\n{doc_text}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )

    with latency.measure("6. LLM (Groq) Response"):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

    return response.choices[0].message.content
