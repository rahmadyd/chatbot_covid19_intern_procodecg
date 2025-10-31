import streamlit as st
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))  
src_path = os.path.join(project_root, "src")  

print(f"🔍 Debug Path:")
print(f"Current dir: {current_dir}")
print(f"Project root: {project_root}")
print(f"Src path: {src_path}")

if src_path not in sys.path:
    sys.path.insert(0, src_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

st.set_page_config(
    page_title="COVID-19 Chatbot",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

hide_streamlit_style = """
    <style>
    /* Sembunyikan sidebar sepenuhnya */
    .css-1d391kg {display: none;}
    section[data-testid="stSidebar"] {display: none !important;}
    
    /* Sembunyikan menu utama */
    #MainMenu {visibility: hidden;}
    
    /* Sembunyikan header */
    header {visibility: hidden;}
    
    /* Sembunyikan footer */
    footer {visibility: hidden;}
    
    /* Sembunyikan deploy button */
    .stDeployButton {display:none;}
    
    /* Sembunyikan hamburger menu */
    #stMainMenu {display: none;}
    
    /* Atur margin untuk kompensasi sidebar yang hilang */
    .main .block-container {
        padding-top: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    </style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🦠 COVID-19 Chatbot Indonesia")
st.markdown("### Selamat datang di pusat informasi COVID-19 Indonesia! 🇮🇩")

st.markdown("### 🧭 Menu Navigasi")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🏠 **Home**", use_container_width=True):
        st.page_link("app.py", label="Home")

with col2:
    if st.button("💬 **Chat**", use_container_width=True):
        st.page_link("pages/01_chat.py", label="Chat")

with col3:
    if st.button("🔍 **Debug**", use_container_width=True):
        st.page_link("pages/02_retrieval_debug.py", label="Debug")

with col4:
    if st.button("⚙️ **Config**", use_container_width=True):
        st.page_link("pages/03_config_tester.py", label="Config")

with col5:
    if st.button("🧹 **Cache**", use_container_width=True):
        st.page_link("pages/04_clear_cache.py", label="Cache")

st.markdown("---")

st.markdown("""
<div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 20px 0;'>
<h4 style='color: #2E86AB;'>🎯 Fitur Utama:</h4>
<ul>
<li>💬 <b>Chat Interaktif</b> - Tanya jawab seputar COVID-19 Indonesia</li>
<li>🔍 <b>Debug Retrieval</b> - Lihat bagaimana sistem menemukan informasi</li>
<li>⚙️ <b>Tes Konfigurasi</b> - Periksa pengaturan sistem</li>
<li>🧹 <b>Clear Cache</b> - Bersihkan cache aplikasi</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("### 💡 Mulai dengan:")
if st.button("🚀 Pergi ke Chatbot", type="primary", use_container_width=True):
    st.switch_page("pages/01_chat.py")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>🤖 Dibangun dengan RAG Technology | 📊 Data COVID-19 Indonesia</div>", unsafe_allow_html=True)