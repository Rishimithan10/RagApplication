# 📚 RagApplication

An end-to-end **Retrieval-Augmented Generation (RAG)** application that enables intelligent question answering over uploaded PDF documents using hybrid retrieval, LLM generation, and built-in response quality evaluation.

---

## 🚀 Features

- 📄 **PDF Document Upload** – Extract and process any PDF for querying
- 🔍 **Hybrid Retrieval** – Combines dense vector search (Pinecone) + sparse BM25 for superior retrieval accuracy
- 🤖 **Groq LLM (Llama 3.3)** – Fast, free, GPT-3.5 level responses via Groq's LPU inference
- 🧠 **HuggingFace Embeddings** – `all-MiniLM-L6-v2` for semantic text embeddings
- 📊 **RAGAS-style Evaluation** – Per-query scoring of Faithfulness, Answer Relevancy, and Context Precision
- ⏱️ **Latency Tracking** – End-to-end breakdown of embedding, retrieval, and LLM response times

---

## 🏗️ Architecture Overview

```
PDF Upload
    │
    ▼
Text Extraction (pdfminer)
    │
    ▼
Chunking (100-word fixed windows)
    │
    ▼
Embedding (all-MiniLM-L6-v2, 384-dim)
    │
    ▼
Pinecone Upsert + BM25 Index (in-memory)
    │
    │  ◄── User asks question
    ▼
Query Embedding
    │
    ▼
Hybrid Retrieval: Dense (Pinecone) + Sparse (BM25)
Score = 0.5 × cosine_similarity + 0.5 × BM25_score
    │
    ▼
Groq Llama 3.3 → Answer
    │
    ▼
RAGAS Evaluation (Faithfulness / Relevancy / Precision)
```

---

## 📊 Performance

| Metric | Value |
|---|---|
| Faithfulness | 1.00 |
| Answer Relevancy | 1.00 |
| Context Precision | 0.85 |
| End-to-end Query Latency | ~570ms |
| BM25 Retrieval Latency | 0.0002s |
| LLM (Groq) Response | ~0.24s |

---

## 📂 Project Structure

```
RagApplication/
│
├── app.py                  # Main Streamlit app
├── config.py               # Loads env variables
├── requirements.txt
├── .env                    # API keys (not committed)
│
└── utils/
    ├── pdf_extract.py      # PDF text extraction
    ├── chunks.py           # Text chunking
    ├── embeddings.py       # HuggingFace embeddings
    ├── vector_store.py     # Pinecone + BM25 hybrid retrieval
    ├── qa_engine.py        # Groq LLM answer generation
    ├── ragas_eval.py       # Response quality evaluation
    └── latency.py          # Latency measurement utility
```

---

## ⚙️ Setup

**1. Clone the repository:**
```bash
git clone https://github.com/Rishimithan10/RagApplication.git
cd RagApplication
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Create a `.env` file:**
```env
pinecone_key=your_pinecone_api_key
hugging_face=your_huggingface_token
GROQ_API_KEY=your_groq_api_key
```

**4. Run the app:**
```bash
streamlit run app.py
```

---

## 🔑 API Keys Required

| Service | Purpose | Free? |
|---|---|---|
| [Pinecone](https://pinecone.io) | Vector database | ✅ Free tier |
| [Groq](https://console.groq.com) | LLM inference | ✅ Free |
| [HuggingFace](https://huggingface.co/settings/tokens) | Embeddings | ✅ Free |

---

## 👨‍💻 Author

**Rishimithan Kannan**
- 📧 rishimithan@gmail.com
- 🐙 [github.com/Rishimithan10](https://github.com/Rishimithan10)
- 💼 [linkedin.com/in/rishimithan-kannan](https://linkedin.com/in/rishimithan-kannan)