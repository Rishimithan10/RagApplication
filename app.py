import streamlit as st
from utils import pdf_extract, chunks as chunker, vector_store, qa_engine
import os
import tempfile
import time

st.set_page_config(page_title="Document Chat Assistant", layout="centered")

st.title("💬 Document Chat Assistant")

# Sidebar
user_id = st.sidebar.text_input("User ID", value="user123")
name=st.sidebar.text_input("Name",value="Rishimithan Kannan")
st.sidebar.markdown("---")

# === Upload Resume ===
st.header("📄 Upload Your Document")
uploaded_file = st.file_uploader("Choose a PDF Document", type=["pdf"])

if uploaded_file and "resume_name" not in st.session_state:
    resume_name = uploaded_file.name.replace(".pdf", "")
    st.session_state.resume_name = resume_name

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # Extract text and chunk
    text = pdf_extract.extract_text_from_pdf(tmp_path)
    if not text:
        st.error("❌ Failed to read the PDF. Please upload a different one.")
        st.stop()

    chunks = chunker.chunk_text(text)
    vector_store.store_chunks(chunks, user_id, resume_name)
    st.success(f"✅ Document `{resume_name}` processed and indexed!")

    os.remove(tmp_path)

# === Initialize chat history ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === Chat Interface ===
if "resume_name" in st.session_state:
    st.markdown("---")
    st.header("💬 Chat With Your Document")

    user_input = st.chat_input("Ask a question about your Document...")
    if user_input:
        resume_name = st.session_state.resume_name

        # Store user question
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Get relevant chunks and generate answer
        with st.spinner("Thinking..."):
            retrieved_chunks = vector_store.retrieve_similar_chunks(user_input, user_id, resume_name)
            if not retrieved_chunks:
                answer = "⚠️ Sorry, I couldn't find relevant info in your document."
            else:
                answer = qa_engine.generate_answer(retrieved_chunks, user_input)

        # Store assistant's answer
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # === Render chat history ===
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            if chat["role"] == "assistant":
                for line in chat["content"].split("\n"):
                    if line.strip():
                        st.markdown(line)
                        time.sleep(0.5)  # Optional delay for typewriter effect
            else:
                st.markdown(chat["content"])

else:
    st.info("📥 Upload your document to start chatting.")
