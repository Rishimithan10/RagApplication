from utils.embeddings import embed_text
from pinecone import Pinecone, ServerlessSpec
import os
from config import pinecone_key
pc = Pinecone(api_key=pinecone_key)

index_name = "resume-index-sbert"  # new name
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",  # or "dotproduct" or "euclidean"
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

def store_chunks(chunks, user_id, resume_name):
    vectors = []
    for i, chunk in enumerate(chunks):
        vector_id = f"{user_id}_{resume_name}_chunk_{i}"
        embedding = embed_text(chunk)[0].tolist()  
        metadata = {
            "user": user_id,
            "resume_name": resume_name,
            "text": chunk
        }
        vectors.append({"id": vector_id, "values": embedding, "metadata": metadata})
    
    index.upsert(vectors=vectors)

def retrieve_similar_chunks(question, user_id, resume_name, top_k=3):
    query_vec = embed_text(question)[0].tolist()  # ✅ Converts ndarray to list
    result = index.query(
        vector=query_vec,
        top_k=top_k,
        include_metadata=True,
        filter={
            "user": {"$eq": user_id},
            "resume_name": {"$eq": resume_name}
        }
    )
    return [match['metadata']['text'] for match in result['matches']]