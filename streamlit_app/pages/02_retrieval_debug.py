# pages/02_retrieval_debug.py
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
src_path = os.path.join(project_root, "src")

print(f"🔍 Project root: {project_root}")

if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
retriever_path = os.path.join(project_root, "src", "retriever.py")

try:
    from src.retriever import Retriever
    print("✅ Retriever imported via normal import")
except ImportError as e:
    st.error(f"❌ Normal import failed: {e}")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("retriever", retriever_path)
        retriever_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(retriever_module)
        Retriever = retriever_module.Retriever
        st.success("✅ Retriever imported via fallback")
    except Exception as fallback_error:
        st.error(f"❌ Fallback import also failed: {fallback_error}")
        st.stop()

from src import config

st.set_page_config(page_title="🔍 Retrieval Debug", page_icon="🧩")

st.title("🔍 Retrieval Debugger")

st.write("""
Gunakan halaman ini untuk mengetes hasil pencarian dari **Retriever (FAISS + Embedding)**  
Masukkan pertanyaan, lalu lihat dokumen mana saja yang dianggap paling relevan.
""")

faiss_path = os.path.join(project_root, "faiss", "faiss_textcovid19.index")
texts_path = os.path.join(project_root, "faiss", "faiss_textcovid19_texts.json")

with st.expander("🔧 Debug File Status"):
    st.write(f"Project root: `{project_root}`")
    st.write(f"FAISS index path: `{faiss_path}`")
    st.write(f"FAISS exists: `{os.path.exists(faiss_path)}`")
    st.write(f"Texts path: `{texts_path}`")
    st.write(f"Texts exists: `{os.path.exists(texts_path)}`")
    st.write(f"Retriever path: `{retriever_path}`")
    st.write(f"Retriever exists: `{os.path.exists(retriever_path)}`")

@st.cache_resource
def load_retriever():
    try:
        retriever = Retriever()
        st.success("✅ Retriever berhasil dimuat!")
        return retriever
    except Exception as e:
        st.error(f"❌ Gagal memuat retriever: {e}")
        return None

retriever = load_retriever()

if retriever is None:
    st.error("""
    ❌ **Retriever gagal dimuat!** 
    
    Kemungkinan penyebab:
    1. File FAISS index tidak ditemukan
    2. File texts.json tidak ditemukan  
    3. Model embedding tidak bisa di-download
    4. Ada error di kode retriever
    
    **Solusi:**
    - Pastikan sudah run `create_embeddings.py` untuk membuat index
    - Cek folder `faiss/` ada file `faiss_textcovid19.index` dan `faiss_textcovid19_texts.json`
    - Cek koneksi internet untuk download model
    """)
    st.stop()

def simple_display_results(results, query, search_method):
    """Fungsi sederhana untuk menampilkan hasil pencarian"""
    if not results:
        st.error("❌ Tidak ada dokumen yang ditemukan dengan threshold saat ini.")
        return
    
    st.success(f"✅ Ditemukan {len(results)} hasil dari FAISS:")
    
    for i, res in enumerate(results, 1):
        with st.expander(f"Hasil {i} - Score: {res.get('score', 'N/A')}", expanded=i==1):
            st.write("**Struktur data:**", res)
            st.write("---")
            st.write("**Teks:**")
            st.write(res.get('text', 'Teks tidak tersedia'))

if 'test_query' not in st.session_state:
    st.session_state.test_query = ""

query = st.text_input("Masukkan pertanyaan tentang COVID-19 di Indonesia:", 
                     placeholder="Contoh: gejala COVID-19",
                     value=st.session_state.test_query)

results = None

if st.button("🔍 Coba Pencarian Sederhana", use_container_width=True) and query:
    with st.spinner("🔍 Mencari..."):
        try:
            results = retriever.search(query)
            st.write("🔍 **Debug Search Results:**", results)  
            
        except Exception as e:
            st.error(f"❌ Error saat search: {e}")

if results is not None:
    simple_display_results(results, query, "Normal Search")

st.markdown("---")
st.markdown("### 🧪 Testing Sederhana")

test_queries = ["gejala COVID-19", "vaksinasi"]

col1, col2 = st.columns(2)
with col1:
    if st.button(test_queries[0], use_container_width=True):
        st.session_state.test_query = test_queries[0]
        st.rerun()
with col2:
    if st.button(test_queries[1], use_container_width=True):
        st.session_state.test_query = test_queries[1]
        st.rerun()