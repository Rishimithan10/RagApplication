import streamlit as st
import os
import tempfile
import time

from utils import pdf_extract, chunks as chunker, vector_store, qa_engine, latency
from utils.ragas_eval import evaluate_rag
from config import groq_api_key

st.set_page_config(page_title="Document Chat Assistant", layout="centered")

st.sidebar.title("💬 Doc Chat Assistant")
st.sidebar.markdown("---")

# === Upload Document ===
st.header("📄 Upload Your Document")
uploaded_file = st.file_uploader("Choose a PDF Document", type=["pdf"])

if uploaded_file:
    st.session_state.doc_name = None
    doc_name = uploaded_file.name.replace(".pdf", "")
    st.session_state.doc_name = doc_name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    latency.reset()
    text = pdf_extract.extract_text_from_pdf(tmp_path)
    if not text:
        st.error("❌ Failed to read PDF.")
        st.stop()

    chunks = chunker.chunk_text(text)
    vector_store.store_chunks(chunks, "default_user", doc_name)
    st.success(f"✅ Document '{doc_name}' processed and ready for chat!")
    os.remove(tmp_path)

    upload_timings = latency.get_all()
    with st.expander("⏱️ Upload Latency Breakdown"):
        for step, seconds in upload_timings.items():
            st.markdown(f"- **{step}**: `{seconds}s`")

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

        latency.reset()
        overall_start = time.perf_counter()

        with st.spinner("Thinking..."):
            retrieved_chunks = vector_store.retrieve_similar_chunks(user_input, "default_user", doc_name)
            if not retrieved_chunks:
                answer = "⚠️ Sorry, no relevant info found in the document."
                ragas_scores = None
            else:
                answer = qa_engine.generate_answer(retrieved_chunks, user_input)

        overall_end = time.perf_counter()
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.session_state["last_latency"] = latency.get_all()
        st.session_state["last_latency_total"] = round(overall_end - overall_start, 4)

        # Run evaluation after answer is ready
        if retrieved_chunks:
            with st.spinner("Evaluating response quality..."):
                ragas_scores = evaluate_rag(user_input, answer, retrieved_chunks, groq_api_key)
            st.session_state["last_ragas"] = ragas_scores
        else:
            st.session_state["last_ragas"] = None

# === Render Chat History ===
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

# === RAGAS Evaluation Scores ===
if st.session_state.get("last_ragas"):
    scores = st.session_state["last_ragas"]

    if "error" in scores:
        with st.expander("📊 Evaluation Scores"):
            st.warning(f"Evaluation error: {scores['error']}")
    else:
        with st.expander("📊 Response Quality Evaluation"):

            # Score cards
            col1, col2, col3 = st.columns(3)
            col1.metric("Faithfulness",      f"{scores['faithfulness']['score']:.2f}",
                        help="Is the answer grounded in the document chunks?")
            col2.metric("Answer Relevancy",  f"{scores['answer_relevancy']['score']:.2f}",
                        help="Does the answer address the question?")
            col3.metric("Context Precision", f"{scores['context_precision']['score']:.2f}",
                        help="Were the right chunks retrieved?")

            st.markdown("---")

            # Detailed reasons
            for metric, label in [
                ("faithfulness",      "Faithfulness"),
                ("answer_relevancy",  "Answer Relevancy"),
                ("context_precision", "Context Precision"),
            ]:
                val    = scores[metric]["score"]
                reason = scores[metric]["reason"]

                if val >= 0.8:
                    st.success(f"✅ **{label}** ({val}) — {reason}")
                elif val >= 0.5:
                    st.warning(f"⚠️ **{label}** ({val}) — {reason}")
                else:
                    st.error(f"❌ **{label}** ({val}) — {reason}")

# === Latency Breakdown ===
if "last_latency" in st.session_state and st.session_state.chat_history:
    with st.expander("⏱️ Query Latency Breakdown"):
        for step, seconds in st.session_state["last_latency"].items():
            st.markdown(f"- **{step}**: `{seconds}s`")
        st.markdown(f"- **Total (end-to-end)**: `{st.session_state['last_latency_total']}s`")
