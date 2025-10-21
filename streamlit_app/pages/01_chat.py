# pages/01_chat.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from src.retriever import Retriever
from src.chatbot import load_generation_model, generate_answer

st.set_page_config(page_title="Chatbot", page_icon="🦠")

st.title("💬 Chatbot COVID-19 di Indonesia")

# ==============================
# 1️⃣ Inisialisasi retriever dan generator
# ==============================
@st.cache_resource
def load_component():
    retriever = Retriever()
    generator = load_generation_model()
    return retriever, generator

retriever, generator = load_component()

# ==============================
# 2️⃣ Input pertanyaan dari user
# ==============================
query = st.text_input("Tanya tentang COVID-19 di Indonesia:")

# ==============================
# 3️⃣ Jika user tekan submit → jalankan retrieval dan generate
# ==============================
if st.button("Send", use_container_width=True):
    if not query.strip():
        st.warning("Masukkan pertanyaan terlebih dahulu.")
    else:
        with st.spinner("🔍 Mencari jawaban..."):
            retrieved_docs = retriever.search(query)
            contexts = [doc["text"] for doc in retrieved_docs]
            answer = generate_answer(query, contexts, generator, max_tokens=300)

        # tampilkan hasil
        st.markdown("### ✨ Jawaban:")
        st.success(answer)

        with st.expander("🔍 Lihat konteks yang digunakan"):
            for i, doc in enumerate(retrieved_docs, 1):
                st.markdown(f"**Konteks {i}:** {doc['text']}")
