from utils.embeddings import embed_text
from pinecone import Pinecone, ServerlessSpec
import os
import streamlit as st
import json
from datetime import date

today = date.today()


from config import pinecone_key
pc = Pinecone(api_key=pinecone_key)


index_name="doc-index"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",  
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

def store_chunks(chunks, user_id, doc_name):
    vectors = []
    for i, chunk in enumerate(chunks):
        vector_id = f"{user_id}_{doc_name}_chunk_{i}"
        embedding = embed_text(chunk)[0].tolist()  
        metadata = {
            "user": user_id,
            "document_name": doc_name,
            "text": chunk,
            "date": today.isoformat()
        }
        vectors.append({"id": vector_id, "values": embedding, "metadata": metadata})
    
    index.upsert(vectors=vectors)

def retrieve_similar_chunks(question, user_id, doc_name, top_k=3):
    query_vec = embed_text(question)[0].tolist()  # ✅ Converts ndarray to list
    result = index.query(
        vector=query_vec,
        top_k=top_k,
        include_metadata=True,
        filter={
            "user": {"$eq": user_id},
            "document_name": {"$eq": doc_name}
        }
    )
    return [match['metadata']['text'] for match in result['matches']]

def get_next_version(user_id, base_doc_name):
    index = pc.Index("doc-index")
    prefix = f"{user_id}_{base_doc_name}_v"
    existing = index.describe_index_stats()["namespaces"].get(user_id, {}).get("vectors", [])

    versions = []
    for vec_id in existing:
        if vec_id.startswith(prefix):
            try:
                version_str = vec_id.split("_v")[-1].split("_")[0]
                version = int(version_str)
                versions.append(version)
            except ValueError:
                continue

    next_version = max(versions, default=0) + 1
    return f"{user_id}_{base_doc_name}_v{next_version}"