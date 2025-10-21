# 02_retrieval_debug.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from src.retriever import Retriever

st.set_page_config(page_title = "🔍 Retrieval Debug", page_icon="🧩")

st.title("🔍 Retrieval Debugger")

st.write("""
Gunakan halaman ini untuk mengetes hasil pencarian dari **Retriever (FAISS + Embedding)**  
Masukkan pertanyaan, lalu lihat dokumen mana saja yang dianggap paling relevan.
""")
# TODO(1): Buat retriever instance
# retriever = ...
@st.cache_resource

def load_retriever():
    return Retriever()

retriever = load_retriever()

# TODO(2): Input query dari user
# query = st.text_input("Masukkan pertanyaan:")
query = st.text_input("Masukkan pertanyaan tentang COVID-19 di Indonesia")

# TODO(3): Jalankan retrieve() daan tampilkan hasil teks
# if st.button("Lihat hasil"):
#     results = ...
#     st.write(results)
if st.button("Hasil", use_container_width=True):
    if not query.strip():
        st.warning("Masukkan pertanyaan...")
    else:
        with st.spinner("🔍 Sedang mencari dokumen yang relevan..."):
            results = retriever.search(query)
            
    if not results:
        st.error("Tidak dapat menemukan jawaban.")
    else:
        st.success(f"Menampilkan {len(results)} hasil teratas dari FAISS:")
        for i, res in enumerate(results, 1):
            st.markdown(f"### 📄 Hasil {i}")
            st.markdown(f"**Skor:** `{res['score']:.4f}`")
            st.markdown(f"**Teks:** {res['text']}")
            st.markdown("---")
