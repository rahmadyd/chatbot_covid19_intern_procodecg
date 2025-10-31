import streamlit as st
import os

st.set_page_config(
    page_title="Clear Cache",
    page_icon="🧹"
)

st.title("🧹 Pembersihan Cache Streamlit")

st.markdown("""
Halaman ini berfungsi untuk menghapus semua data yang disimpan oleh Streamlit 
menggunakan decorator `@st.cache_resource` dan `@st.cache_data`. 

Ini diperlukan setelah Anda melakukan perubahan pada:
* **Path file** (misalnya `INDEX_PATH`, `TEXT_PATH`)
* **Konfigurasi Model** (misalnya `top_k`, `temperature`)
* **Logic Model** (`retriever.py` atau `generation.py`)
""")

st.warning("Perhatian: Tindakan ini akan memaksa semua komponen (seperti FAISS Index dan Model) untuk dimuat ulang saat halaman Chat dibuka.")

if st.button("🔴 Hapus Semua Cache dan Reset Aplikasi", use_container_width=True):
    try:
        st.cache_data.clear()
        
        st.cache_resource.clear()
        
        st.success("✅ Cache berhasil dibersihkan! Silakan kembali ke halaman Chat (01_chat) untuk memuat ulang komponen.")
        
    except Exception as e:
        st.error(f"❌ Error membersihkan cache: {e}")

st.markdown("---")
st.markdown("""
### 📝 Instruksi Setelah Clear Cache:
1. Kembali ke halaman **Chat Utama**
2. Sistem akan memuat ulang semua komponen
3. Ajukan pertanyaan untuk test
""")