# 📚 AI Applications Monorepo

A collection of AI-powered applications showcasing **Retrieval-Augmented Generation (RAG)**, **Fine-Tuned Large Language Models**, **Agentic AI**, and **API-based deployment architectures**.

---

## 🚀 Projects

### 📄 RagApplication

An end-to-end **Retrieval-Augmented Generation (RAG)** application that enables intelligent question answering over uploaded PDF documents using hybrid retrieval, LLM generation, and built-in response quality evaluation.

### 🤖 ML Agent

A **Fine-Tuned Llama 3B Agent** powered by LangChain and served through FastAPI. The project uses LoRA fine-tuning and is designed for containerized deployment using Docker.

---

# 📄 Project 1 — RagApplication

## 🚀 Features

* 📄 **PDF Document Upload** – Extract and process any PDF for querying
* 🔍 **Hybrid Retrieval** – Combines dense vector search (Pinecone) + sparse BM25 for superior retrieval accuracy
* 🤖 **Groq LLM (Llama 3.3)** – Fast, free, GPT-3.5 level responses via Groq's LPU inference
* 🧠 **HuggingFace Embeddings** – `all-MiniLM-L6-v2` for semantic text embeddings
* 📊 **RAGAS-style Evaluation** – Per-query scoring of Faithfulness, Answer Relevancy, and Context Precision
* ⏱️ **Latency Tracking** – End-to-end breakdown of embedding, retrieval, and LLM response times

---

## 🏗️ Architecture Overview

```text
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

| Metric                   | Value   |
| ------------------------ | ------- |
| Faithfulness             | 1.00    |
| Answer Relevancy         | 1.00    |
| Context Precision        | 0.85    |
| End-to-end Query Latency | ~570ms  |
| BM25 Retrieval Latency   | 0.0002s |
| LLM (Groq) Response      | ~0.24s  |

---

# 🤖 Project 2 — ML Agent

A LangChain-powered AI agent built on a fine-tuned Llama 3B model and exposed through FastAPI for scalable deployment.

## 🚀 Features

* 🦙 **Llama 3B Fine-Tuning** – LoRA-based domain adaptation
* 🔗 **LangChain Agent** – Tool calling and reasoning workflows
* ⚡ **FastAPI Backend** – High-performance inference API
* 🐳 **Docker Deployment** – Containerized production-ready deployment
* 📦 **Modular Architecture** – Separate model, agent, and API layers

---

## 🏗️ Architecture Overview

```text
User Request
    │
    ▼
FastAPI (main.py)
    │
    ▼
LangChain Agent (agent.py)
    │
    ▼
Fine-Tuned Llama 3B
(model.py + adapter/)
    │
    ▼
Generated Response
```

---

## 📂 Repository Structure

```text
RagApplication/
│
├── RagApplication/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── .env
│   └── utils/
│       ├── pdf_extract.py
│       ├── chunks.py
│       ├── embeddings.py
│       ├── vector_store.py
│       ├── qa_engine.py
│       ├── ragas_eval.py
│       └── latency.py
│
└── ml_agent/
    ├── model.py
    ├── agent.py
    ├── main.py
    ├── adapter/
    └── requirements.txt
```


---

## ⚙️ Setup

### RagApplication

```bash
cd RagApplication
pip install -r requirements.txt
streamlit run app.py
```

### ML Agent

```bash
cd ml_agent
pip install -r requirements.txt
python main.py
```

### Docker (ML Agent)

```bash
docker build -t ml-agent .
docker run -p 8000:8000 ml-agent
```

---

## 🔑 API Keys Required

| Service     | Purpose             | Free?       |
| ----------- | ------------------- | ----------- |
| Pinecone    | Vector Database     | ✅ Free Tier |
| Groq        | LLM Inference       | ✅ Free      |
| HuggingFace | Embeddings & Models | ✅ Free      |

---

## 👨‍💻 Author

**Rishimithan Kannan**

* 📧 [rishimithan@gmail.com](mailto:rishimithan@gmail.com)
* 🐙 https://github.com/Rishimithan10
* 💼 https://linkedin.com/in/rishimithan-kannan
