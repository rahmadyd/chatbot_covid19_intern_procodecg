import streamlit as st

st.set_page_config(
    page_title="COVID-19 Chatbot",
    page_icon="🦠",
    layout="wide"
)

# 👇 Tambahkan ini
st.sidebar.title("Navigasi")
st.sidebar.page_link("app.py", label="🏠 Halaman Utama")
st.sidebar.page_link("pages/01_chat.py", label="💬 Chat dengan bot")
st.sidebar.page_link("pages/02_retrieval_debug.py", label="🔍 Debug hasil retrieval")
st.sidebar.page_link("pages/03_config_tester.py", label="⚙️ Tes konfigurasi sistem")

st.title("🧠 COVID-19 Chatbot – Main Page")

st.write("""
Selamat datang di chatbot COVID-19 🇮🇩  
Gunakan menu di sidebar untuk:
1. 💬 Chat dengan bot  
2. 🔍 Debug hasil retrieval  
3. ⚙️ Tes konfigurasi sistem
""")
