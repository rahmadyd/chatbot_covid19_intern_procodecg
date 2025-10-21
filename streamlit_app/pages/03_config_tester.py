# 03_config_tester.py
import streamlit as st
from src import config

st.title("⚙️ Config Tester")

st.write("## Informasi Konfigurasi:")
st.json({
    "Base Dir": config.BASE_DIR,
    "Environment": config.ENV_MODE,
    "Model Config": config.MODEL_CONFIG,
    "Index Path": config.INDEX_PATH,
    "Text Path": config.TEXT_PATH,
})
