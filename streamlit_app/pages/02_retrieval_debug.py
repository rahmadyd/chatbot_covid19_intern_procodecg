# pages/02_retrieval_debug.py
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
src_path = os.path.join(project_root, "src")

print(f"🔍 Project root: {project_root}")

if src_path not in sys.path:
    sys.path.insert(0, src_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st

try:
    from retriever import Retriever
    print("✅ Retriever imported successfully")
except ImportError as e:
    st.error(f"❌ Import failed: {e}")
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
    st.write(f"Src path: `{src_path}`")

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

def advanced_debug_search():
    """Fitur debug advanced untuk test retrieval"""
    st.subheader("🔧 Advanced Debug Search")
    
    debug_query = st.text_input("Masukkan query untuk debug:", "Kapan vaksinasi dimulai?")
    
    if st.button("🔍 Debug Search", key="debug_search"):
        with st.spinner("Debugging..."):
            try:
                # Gunakan search_with_debug yang baru
                results, debug_info = retriever.search_with_debug(debug_query)
                
                # Tampilkan debug info
                st.info(f"**Debug Info:**")
                st.json(debug_info)
                
                # Tampilkan results
                if results:
                    st.success(f"✅ Found {len(results)} relevant documents")
                    
                    for i, result in enumerate(results):
                        with st.expander(f"Document {i+1} - Score: {result['score']:.3f}", expanded=i==0):
                            st.write(f"**Relevance Score:** {result.get('relevance_score', 'N/A')}")
                            st.write(f"**Original Score:** {result.get('original_score', 'N/A')}")
                            st.write(f"**Text:** {result['text']}")
                            
                            # Check if contains expected keywords
                            text_lower = result['text'].lower()
                            if 'vaksinasi' in debug_query.lower():
                                if any(kw in text_lower for kw in ['januari', '2021', 'vaksinasi', 'mulai']):
                                    st.success("🎯 Contains vaksinasi information!")
                                else:
                                    st.warning("⚠️ No vaksinasi keywords found")
                            if 'covid' in debug_query.lower():
                                if any(kw in text_lower for kw in ['covid', 'corona', 'virus', 'sars']):
                                    st.success("🎯 Contains COVID information!")
                                    
                else:
                    st.error("❌ No documents found!")
                    
                    # 🚨 SHOW WHAT'S WRONG - Check knowledge base content
                    st.subheader("🚨 Knowledge Base Analysis")
                    
                    # Cek berapa banyak dokumen di knowledge base
                    st.write(f"Total documents in FAISS: {len(retriever.texts) if retriever.texts else 0}")
                    
                    # Show sample of what's actually there
                    if retriever.texts:
                        st.write("**Sample documents:**")
                        for i, text in enumerate(retriever.texts[:5]):
                            st.write(f"{i+1}. {text[:150]}...")
                    else:
                        st.error("❌ Knowledge base is EMPTY!")
                    
            except Exception as e:
                st.error(f"❌ Debug error: {e}")
                import traceback
                st.error(f"Traceback: {traceback.format_exc()}")

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

# Panggil advanced debug
advanced_debug_search()

st.markdown("---")
st.markdown("### 🧪 Testing Sederhana")

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
            
        except Exception as e:
            st.error(f"❌ Error saat search: {e}")

if results is not None:
    simple_display_results(results, query, "Normal Search")

test_queries = ["gejala COVID-19", "vaksinasi", "program PEN", "isolasi mandiri"]

cols = st.columns(4)
for i, test_query in enumerate(test_queries):
    with cols[i]:
        if st.button(test_query, use_container_width=True):
            st.session_state.test_query = test_query
            st.rerun()