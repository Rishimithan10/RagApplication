# from utils.embeddings import embed_text
# from utils import latency
# from pinecone import Pinecone, ServerlessSpec
# from datetime import date
# from config import pinecone_key

# today = date.today()

# pc = Pinecone(api_key=pinecone_key)

# index_name = "doc-index"
# if index_name not in pc.list_indexes().names():
#     pc.create_index(
#         name=index_name,
#         dimension=384,
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1")
#     )

# index = pc.Index(index_name)


# def store_chunks(chunks, user_id, doc_name):
#     with latency.measure("3. Embedding + Upsert (Store)"):
#         vectors = []
#         for i, chunk in enumerate(chunks):
#             vector_id = f"{user_id}_{doc_name}_chunk_{i}"
#             embedding = embed_text(chunk)[0].tolist()
#             metadata = {
#                 "user": user_id,
#                 "document_name": doc_name,
#                 "text": chunk,
#                 "date": today.isoformat()
#             }
#             vectors.append({"id": vector_id, "values": embedding, "metadata": metadata})
#         index.upsert(vectors=vectors)


# def retrieve_similar_chunks(question, user_id, doc_name, top_k=3):
#     with latency.measure("4. Embedding Query"):
#         query_vec = embed_text(question)[0].tolist()

#     with latency.measure("5. Pinecone Retrieval"):
#         result = index.query(
#             vector=query_vec,
#             top_k=top_k,
#             include_metadata=True,
#             filter={
#                 "user": {"$eq": user_id},
#                 "document_name": {"$eq": doc_name}
#             }
#         )
#     return [match['metadata']['text'] for match in result['matches']]


# def get_next_version(user_id, base_doc_name):
#     index = pc.Index("doc-index")
#     prefix = f"{user_id}_{base_doc_name}_v"
#     existing = index.describe_index_stats()["namespaces"].get(user_id, {}).get("vectors", [])

#     versions = []
#     for vec_id in existing:
#         if vec_id.startswith(prefix):
#             try:
#                 version_str = vec_id.split("_v")[-1].split("_")[0]
#                 version = int(version_str)
#                 versions.append(version)
#             except ValueError:
#                 continue

#     next_version = max(versions, default=0) + 1
#     return f"{user_id}_{base_doc_name}_v{next_version}"
from utils.embeddings import embed_text
from utils import latency
from pinecone import Pinecone, ServerlessSpec
from rank_bm25 import BM25Okapi
from datetime import date
from config import pinecone_key
import numpy as np

today = date.today()

pc = Pinecone(api_key=pinecone_key)

index_name = "rag-index"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# ── In-memory BM25 store (per session) ──────────────────────────────────────
# { "user_id::doc_name": { "chunks": [...], "bm25": BM25Okapi } }
_bm25_store = {}


def _store_key(user_id, doc_name):
    return f"{user_id}::{doc_name}"


def store_chunks(chunks, user_id, doc_name):
    with latency.measure("3. Embedding + Upsert (Store)"):
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

    # Build BM25 index in memory for this doc
    tokenized = [chunk.lower().split() for chunk in chunks]
    _bm25_store[_store_key(user_id, doc_name)] = {
        "chunks": chunks,
        "bm25": BM25Okapi(tokenized)
    }


def retrieve_similar_chunks(question, user_id, doc_name, top_k=3, alpha=0.5):
    """
    Hybrid retrieval: combines Dense (Pinecone) + Sparse (BM25) scores.
    alpha=0.5 means equal weight. Increase alpha to favour dense, decrease for BM25.
    """

    # ── Step 1: Dense retrieval from Pinecone ───────────────────────────────
    with latency.measure("4. Embedding Query"):
        query_vec = embed_text(question)[0].tolist()

    with latency.measure("5. Pinecone Dense Retrieval"):
        # Fetch more candidates than top_k so reranking has room to work
        result = index.query(
            vector=query_vec,
            top_k=top_k * 3,  # fetch 3x, rerank down to top_k
            include_metadata=True,
            filter={
                "user": {"$eq": user_id},
                "document_name": {"$eq": doc_name}
            }
        )
    dense_matches = result["matches"]

    # ── Step 2: BM25 sparse retrieval ───────────────────────────────────────
    with latency.measure("6. BM25 Sparse Retrieval"):
        key = _store_key(user_id, doc_name)
        if key in _bm25_store:
            store = _bm25_store[key]
            bm25_scores = store["bm25"].get_scores(question.lower().split())
            all_chunks = store["chunks"]

            # Normalize BM25 scores to [0, 1]
            max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
            bm25_norm = bm25_scores / max_bm25

            # Build a lookup: chunk_text -> bm25 score
            bm25_lookup = {chunk: float(bm25_norm[i]) for i, chunk in enumerate(all_chunks)}
        else:
            # BM25 not available (e.g. app restarted), fall back to dense only
            bm25_lookup = {}

    # ── Step 3: Combine scores ───────────────────────────────────────────────
    with latency.measure("7. Hybrid Reranking"):
        scored = []
        for match in dense_matches:
            chunk_text = match["metadata"]["text"]
            dense_score = float(match["score"])                        # cosine similarity [0,1]
            sparse_score = bm25_lookup.get(chunk_text, 0.0)           # BM25 normalized [0,1]
            hybrid_score = alpha * dense_score + (1 - alpha) * sparse_score
            scored.append((hybrid_score, chunk_text))

        # Sort by hybrid score descending, take top_k
        scored.sort(key=lambda x: x[0], reverse=True)

    return [chunk for _, chunk in scored[:top_k]]


def get_next_version(user_id, base_doc_name):
    index = pc.Index("rag-index")
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