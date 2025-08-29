# 📚 RagApplication  

An end-to-end **Retrieval-Augmented Generation (RAG)** application that combines **vector search**, **authentication**, and **LLMs** for intelligent question answering.  

---

## 🚀 Features  
- 🔍 **Vector Search with Pinecone** – Efficient semantic search over your documents.  
- 🔑 **Authentication with Firebase** – Secure login and user management.  
- 🤖 **Hugging Face Transformers** – For text embeddings & NLP tasks.  
- 💡 **GPT-3.5 API** – For high-quality, context-aware responses.  

---

## 🏗️ Architecture Overview  
1. **User Login** → Firebase Authentication  
2. **Query Input** → User submits a question  
3. **Vector Search** → Query is embedded via Hugging Face models, searched in Pinecone  
4. **Context Injection** → Retrieved documents are combined with the query  
5. **LLM Response** → GPT-3.5 API generates a final answer  

---

## 📖 Usage  
- ✅ Sign up / log in with **Firebase Auth**  
- 📂 Upload or connect your documents  
- ❓ Ask a question in the chat UI  
- 🔍 The system retrieves relevant chunks via **Pinecone**  
- 🤖 The **GPT-3.5 API** generates a contextual response  

---

## 🔮 Roadmap  
- [ ] Add support for **LangChain/LlamaIndex orchestration**  
- [ ] Implement **fine-tuned Hugging Face embeddings**  
- [ ] Multi-user document storage  
- [ ] Streaming responses like **ChatGPT**  

---

## 👨‍💻 Author  
**Rishimithan Kannan**  
- 📧 Email: rishimithan@gmail.com  
 


## 📂 Project Structure  
