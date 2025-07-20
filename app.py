import streamlit as st
import requests
import os
import tempfile
import time
import json

from utils import pdf_extract, chunks as chunker, vector_store, qa_engine, firebase, tokens


st.set_page_config(page_title="Document Chat Assistant", layout="centered")


if "id_token" not in st.session_state:
    saved = tokens.load_tokens()
    if saved:
        st.session_state.id_token = saved["id_token"]
        st.session_state.refresh_token = saved["refresh_token"]
        st.session_state.user_id = saved["user_id"]
        st.session_state.token_expiry = saved["token_expiry"]
        
if "id_token" not in st.session_state:
    st.sidebar.title("Login/Register")
    st.title("💬 Doc Chat Assistant")

    st.markdown("""
    Welcome to the **Doc Chat Assistant** — your intelligent assistant to understand and interact with your PDF documents.  
    <br>
    📄 Simply upload a PDF file — whether it's a resume, report, or academic paper.  
    <br>
    💬 Then, ask any question related to the document — from summaries to specific details.  
    <br>
    🧠 The assistant uses AI to retrieve and generate accurate, context-aware answers directly from the uploaded content.  
    <br>
    Let's get started!
    """, unsafe_allow_html=True)

    # Initialize register form toggle
    if "show_register_form" not in st.session_state:
        st.session_state.show_register_form = False

    # 📋 Register Fields
    if st.session_state.show_register_form:
        st.sidebar.subheader("👤 Create Account")

        first_name = st.sidebar.text_input("First Name", key="register_first_name")
        last_name = st.sidebar.text_input("Last Name", key="register_last_name")
        reg_email = st.sidebar.text_input("Email", key="register_email")
        reg_password = st.sidebar.text_input("Password", type="password", key="register_password")

        if st.sidebar.button("Signup"):
            res = firebase.firebase_signup(reg_email, reg_password, first_name, last_name)

            if "id_token" in res or "idToken" in res:
                st.sidebar.success("✅ Registered. Please log in.")
                st.session_state.show_register_form = False
                st.rerun()
            else:
                error = res.get("error") if isinstance(res, dict) else str(res)
                st.sidebar.error("❌ Registration failed: " + error)

        # Optional: Cancel button to go back to login
        if st.sidebar.button("Back to Login"):
            st.session_state.show_register_form = False
            st.rerun()

    # 🔐 Show login form only if not registering
    if not st.session_state.show_register_form:
        email = st.sidebar.text_input("Email", key="login_email")
        password = st.sidebar.text_input("Password", type="password", key="login_password")
        col1, col2 = st.sidebar.columns(2)

        if col1.button("Login"):
            res = firebase.firebase_login(email, password)
            if "idToken" in res:
                st.session_state.id_token = res["idToken"]
                st.session_state.refresh_token = res["refreshToken"]
                st.session_state.user_id = res["localId"]
                st.session_state.token_expiry = time.time() + int(res["expiresIn"])
                st.session_state.user_email = str(email)
                user_data = firebase.get_user_details(st.session_state.user_id)
                if user_data:
                    st.session_state.first_name = user_data.get("first_name")
                    st.session_state.last_name = user_data.get("last_name")
                tokens.save_tokens({
                    "id_token": st.session_state.id_token,
                    "refresh_token": st.session_state.refresh_token,
                    "user_id": st.session_state.user_id,
                    "token_expiry": st.session_state.token_expiry
                })
                
                st.rerun()
            else:
                st.sidebar.error("❌ Login failed: " + res.get("error", {}).get("message", "Unknown error"))

        if col2.button("Register"):
            st.session_state.show_register_form = True
            st.rerun()

    st.stop()


# === Auto-refresh token if expiring ===
if "id_token" in st.session_state and "token_expiry" in st.session_state:
    if time.time() > st.session_state.token_expiry - 30:
        refresh_result = firebase.refresh_firebase_token(st.session_state.refresh_token)
        if "id_token" in refresh_result:
            st.session_state.id_token = refresh_result["id_token"]
            st.session_state.refresh_token = refresh_result["refresh_token"]
            st.session_state.token_expiry = time.time() + int(refresh_result["expires_in"])

            tokens.save_tokens({
                "id_token": st.session_state.id_token,
                "refresh_token": st.session_state.refresh_token,
                "user_id": st.session_state.user_id,
                "token_expiry": st.session_state.token_expiry
            })
        else:
            st.sidebar.warning("Session expired. Please login again.")
            tokens.delete_tokens()
            st.session_state.clear()
            st.rerun()

st.sidebar.title("💬 Doc Chat Assistant")
user_id=st.session_state.user_id
user_detail=firebase.get_user_details(user_id)

first_name=user_detail["first_name"]
last_name=user_detail["last_name"]
st.sidebar.markdown(f"👋 Welcome, {first_name} {last_name}")


if st.sidebar.button("Logout"):
    tokens.delete_tokens()
    st.session_state.clear()
    st.rerun()

user_id = st.session_state.get("user_id", "anonymous")
st.sidebar.markdown("---")

# === Upload Document ===
st.header("📄 Upload Your Document")
uploaded_file = st.file_uploader("Choose a PDF Document", type=["pdf"])

if uploaded_file:
    # Reset previous document data
    st.session_state.doc_name = None

    doc_name = uploaded_file.name.replace(".pdf", "")
    st.session_state.doc_name = doc_name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    text = pdf_extract.extract_text_from_pdf(tmp_path)
    if not text:
        st.error("❌ Failed to read PDF.")
        st.stop()

    chunks = chunker.chunk_text(text)
    vector_store.store_chunks(chunks, user_id, doc_name)
    st.success(f"✅ Document {doc_name} processed and ready for chat!")
    os.remove(tmp_path)


# === Chat History ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === Chat Interface ===
if "doc_name" in st.session_state:
    st.markdown("---")
    st.header("💬 Chat With Your Document")

    user_input = st.chat_input("Ask a question about your Document...")
    if user_input:
        doc_name = st.session_state.doc_name
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            retrieved_chunks = vector_store.retrieve_similar_chunks(user_input, user_id, doc_name)
            if not retrieved_chunks:
                answer = "⚠️ Sorry, no relevant info found in the document."
            else:
                answer = qa_engine.generate_answer(retrieved_chunks, user_input)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})

for i, chat in enumerate(st.session_state.chat_history):
    with st.chat_message(chat["role"]):
        lines = chat["content"].strip().split("\n")
        is_last_message = (i == len(st.session_state.chat_history) - 1)

        for line in lines:
            if line.strip():
                if is_last_message:
                    placeholder = st.empty()
                    text = ""
                    for char in line.strip():
                        text += char
                        placeholder.markdown(text)
                        time.sleep(0.01)
                    time.sleep(0.3)
                else:
                    st.markdown(line.strip())
