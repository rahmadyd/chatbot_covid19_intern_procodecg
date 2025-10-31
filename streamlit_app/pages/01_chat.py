import sys
import os
import json
import uuid
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
src_path = os.path.join(project_root, "src")

print(f"🔍 Debug Path:")
print(f"Current dir: {current_dir}")
print(f"Project root: {project_root}")
print(f"Src path: {src_path}")

if src_path not in sys.path:
    sys.path.insert(0, src_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import time

try:
    print("🔄 Mencoba import dari src folder...")
    
    from retriever import Retriever
    from generation import load_generation_model, generate_answer
    import config
    
    print("✅ Semua modul berhasil diimport!")
    
except ImportError as e:
    st.error(f"❌ Gagal mengimpor modul: {e}")
    import traceback
    st.error(f"Traceback: {traceback.format_exc()}")
    st.stop()

st.set_page_config(page_title="Chatbot COVID-19", page_icon="🦠", layout="wide")

# ==============================
# 1️⃣ FILE UNTUK MENYIMPAN CHAT ROOMS
# ==============================
CHAT_DATA_FILE = os.path.join(project_root, "data", "chat_rooms.json")

def ensure_data_dir():
    """Pastikan folder untuk menyimpan data ada"""
    os.makedirs(os.path.dirname(CHAT_DATA_FILE), exist_ok=True)

def load_chat_rooms():
    """Load semua chat rooms dari file"""
    ensure_data_dir()
    try:
        if os.path.exists(CHAT_DATA_FILE):
            with open(CHAT_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"❌ Gagal load chat rooms: {e}")
    return {}

def save_chat_rooms(chat_rooms):
    """Simpan semua chat rooms ke file"""
    ensure_data_dir()
    try:
        with open(CHAT_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(chat_rooms, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"❌ Gagal save chat rooms: {e}")

# ==============================
# 2️⃣ INISIALISASI SESSION STATE
# ==============================
if "chat_rooms" not in st.session_state:
    st.session_state.chat_rooms = load_chat_rooms()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "processing" not in st.session_state:
    st.session_state.processing = False

if "rename_mode" not in st.session_state:
    st.session_state.rename_mode = None

# ==============================
# 3️⃣ LOAD COMPONENTS - YANG DIPERBAIKI
# ==============================
@st.cache_resource
def load_components():
    try:
        print("🔄 Loading generation model...")
        generator_id = load_generation_model()  
        
        print("🔄 Loading retriever...")
        retriever = Retriever()  
        
        print(f"✅ Components loaded - Model: {generator_id}")
        return retriever, generator_id
        
    except Exception as e:
        st.error(f"❌ Gagal memuat komponen: {e}")
        import traceback
        st.error(f"Detail error: {traceback.format_exc()}")
        return None, None

# Load components
retriever, generator_id = load_components()

if retriever is None or generator_id is None:
    st.error("""
    ❌ Sistem tidak dapat dimulai. 
    
    **Kemungkinan penyebab:**
    1. File FAISS index tidak ditemukan
    2. File chunks.json struktur tidak sesuai
    3. Ollama server tidak berjalan
    
    **Solusi:**
    - Pastikan file ada di: `D:\\chatbot_covid19_intern_procodecg\\faiss\\`
    - Cek halaman **Debug** untuk info lebih detail
    """)
    st.stop()

# ==============================
# 4️⃣ FUNGSI UTAMA CHAT ROOMS (tetap sama)
# ==============================
def create_new_chat():
    """Buat chat room baru"""
    chat_id = str(uuid.uuid4())[:8]
    st.session_state.current_chat_id = chat_id
    st.session_state.chat_rooms[chat_id] = {
        "title": "Chat Baru",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": [],
        "is_new": True
    }
    save_chat_rooms(st.session_state.chat_rooms)

def delete_chat(chat_id):
    """Hapus chat room"""
    if chat_id in st.session_state.chat_rooms:
        del st.session_state.chat_rooms[chat_id]
        if st.session_state.current_chat_id == chat_id:
            st.session_state.current_chat_id = None
        save_chat_rooms(st.session_state.chat_rooms)
        st.success("🗑️ Chat berhasil dihapus!")
        st.rerun()

def rename_chat(chat_id, new_title):
    """Ganti nama chat room"""
    if chat_id in st.session_state.chat_rooms:
        st.session_state.chat_rooms[chat_id]["title"] = new_title
        save_chat_rooms(st.session_state.chat_rooms)
        st.session_state.rename_mode = None
        st.rerun()

def add_message_to_chat(chat_id, role, content, retrieval_time=None, generation_time=None, sources=None):
    """Tambahkan pesan ke chat room tertentu"""
    if chat_id not in st.session_state.chat_rooms:
        return
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "retrieval_time": retrieval_time,
        "generation_time": generation_time,
        "sources": sources or []
    }
    
    st.session_state.chat_rooms[chat_id]["messages"].append(message)
    save_chat_rooms(st.session_state.chat_rooms)

def extract_source_from_text(text, score, doc_id, rank):
    """Ekstrak informasi sumber langsung dari teks yang di-retrieve"""
    if not isinstance(text, str):
        text = str(text)
        
    clean_text = text.replace('\n', ' ').strip()
    
    sentences = clean_text.split('.')
    if sentences and len(sentences[0]) > 20:
        source_title = sentences[0].strip() + "..."
    else:
        source_title = clean_text[:60] + "..." if len(clean_text) > 60 else clean_text
    
    preview = clean_text[:120] + "..." if len(clean_text) > 120 else clean_text
    
    return {
        "source": f"Referensi #{rank}",
        "title": source_title,
        "preview": preview,
        "score": float(score) if score else 0.0,
        "doc_id": doc_id
    }

def format_sources(sources):
    """Format sumber referensi untuk ditampilkan"""
    if not sources:
        return "**Tidak ada sumber referensi yang ditemukan**"
    
    formatted = "**📚 Sumber Referensi:**\n\n"
    for i, source in enumerate(sources, 1):
        formatted += f"{i}. **{source['title']}**  \n"
        formatted += f"   🎯 Relevansi: `{source['score']:.3f}`  \n"
        formatted += f"   📖 Preview: *{source['preview']}*  \n\n"
    
    return formatted

def process_question(question):
    """Proses pertanyaan dan kembalikan jawaban dengan sumber referensi"""
    try:
        # --- TAHAP 1: RETRIEVAL ---
        start_time = time.time()
        retrieved_docs = retriever.search(question)
        retrieval_time = time.time() - start_time
        
        print(f"🔍 Retrieval found {len(retrieved_docs)} docs, time: {retrieval_time:.2f}s")
        
        # --- TAHAP 2: GENERATION ---
        gen_start = time.time()
        answer = generate_answer(question, retrieved_docs, generator_id)
        generation_time = time.time() - gen_start
        
        print(f"🤖 Generation time: {generation_time:.2f}s")
        
        # --- TAHAP 3: EKSTRAK SUMBER REFERENSI ---
        sources = []
        for i, doc in enumerate(retrieved_docs[:3]):
            if isinstance(doc, dict):
                text = doc.get('text', '')
                score = doc.get('score', 0)
                doc_id = doc.get('doc_id', 0)
                
                source_info = extract_source_from_text(text, score, doc_id, i + 1)
                sources.append(source_info)
        
        return answer, retrieval_time, generation_time, sources
        
    except Exception as e:
        return f"❌ Error: {str(e)}", 0, 0, []
        
# ==============================
# 5️⃣ SIDEBAR - CHAT ROOMS LIST
# ==============================
with st.sidebar:
    st.header("💬 Chat Rooms")
    
    if st.button("➕ Chat Baru", use_container_width=True):
        create_new_chat()
        st.rerun()
    
    st.markdown("---")
    
    if st.session_state.chat_rooms:
        st.markdown("### 📁 Chat History")
        
        sorted_chats = sorted(
            st.session_state.chat_rooms.items(),
            key=lambda x: x[1]["created_at"],
            reverse=True
        )
        
        for chat_id, chat_data in sorted_chats:
            is_active = st.session_state.current_chat_id == chat_id
            
            col1, col2, col3 = st.columns([6, 1, 1])
            
            with col1:
                if st.session_state.rename_mode == chat_id:
                    new_title = st.text_input(
                        "Nama baru:",
                        value=chat_data["title"],
                        key=f"rename_{chat_id}",
                        label_visibility="collapsed"
                    )
                    if st.button("✅", key=f"save_rename_{chat_id}"):
                        if new_title.strip():
                            rename_chat(chat_id, new_title.strip())
                else:
                    if st.button(
                        f"💬 {chat_data['title']}",
                        key=f"chat_{chat_id}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary"
                    ):
                        st.session_state.current_chat_id = chat_id
                        st.rerun()
            
            with col2:
                if st.button("✏️", key=f"rename_btn_{chat_id}"):
                    st.session_state.rename_mode = chat_id
                    st.rerun()
            
            with col3:
                if st.button("🗑️", key=f"delete_{chat_id}"):
                    delete_chat(chat_id)
    
    else:
        st.info("Belum ada chat. Buat chat baru untuk memulai!")
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    st.metric("Total Chats", len(st.session_state.chat_rooms))
    
    if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_rooms:
        current_messages = st.session_state.chat_rooms[st.session_state.current_chat_id]["messages"]
        st.metric("Pesan di Chat Ini", len(current_messages))

# ==============================
# 6️⃣ MAIN CHAT AREA
# ==============================
st.title("💬 Chatbot COVID-19 di Indonesia")

if not st.session_state.current_chat_id:
    st.markdown("""
    <div style='text-align: center; padding: 4rem; color: #666;'>
        <h3>🦠 COVID-19 Indonesia Chatbot</h3>
        <p>Pilih chat yang sudah ada atau buat chat baru untuk memulai percakapan</p>
        <br>
        <div style='display: inline-block; text-align: left;'>
        <b>Fitur:</b><br>
        • 💬 Multiple chat rooms<br>
        • ✏️ Rename chat<br>
        • 🗑️ Hapus chat<br>
        • 💾 Auto-save history<br>
        • 📚 Sumber referensi
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    current_chat = st.session_state.chat_rooms[st.session_state.current_chat_id]
    messages = current_chat["messages"]
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader(f"💬 {current_chat['title']}")
    with col2:
        if st.button("🗑️ Hapus Chat Ini", type="secondary"):
            delete_chat(st.session_state.current_chat_id)
    
    st.caption(f"Dibuat: {current_chat['created_at']}")
    st.markdown("---")
    
    chat_container = st.container()
    
    with chat_container:
        for message in messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
                    if message.get("retrieval_time"):
                        st.caption(f"🕒 {message['timestamp']}")
                    
            elif message["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.markdown(message["content"])
                    
                    if message.get("sources"):
                        with st.expander(f"📚 Lihat {len(message['sources'])} Sumber Referensi", expanded=False):
                            st.markdown(format_sources(message["sources"]))
                    
                    if message.get("retrieval_time") or message.get("generation_time"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.caption(f"⏱️ Retrieval: {message.get('retrieval_time', 0):.2f}s")
                        with col2:
                            st.caption(f"⏱️ Generation: {message.get('generation_time', 0):.2f}s")
                    
                    st.caption(f"🕒 {message['timestamp']}")

    if prompt := st.chat_input("Tanya tentang COVID-19 di Indonesia..."):
        add_message_to_chat(st.session_state.current_chat_id, "user", prompt)
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("🔄 Mencari informasi..."):
                    # Proses pertanyaan
                    answer, retrieval_time, generation_time, sources = process_question(prompt)
                    
                    # Tambahkan jawaban assistant ke chat
                    add_message_to_chat(
                        st.session_state.current_chat_id, 
                        "assistant", 
                        answer, 
                        retrieval_time, 
                        generation_time, 
                        sources
                    )
                    
                    # Tampilkan jawaban
                    st.markdown(answer)
                    
                    # Tampilkan sumber referensi
                    if sources:
                        with st.expander(f"📚 Lihat {len(sources)} Sumber Referensi", expanded=False):
                            st.markdown(format_sources(sources))
                    
                    # Tampilkan metadata
                    if retrieval_time > 0 or generation_time > 0:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.caption(f"⏱️ Retrieval: {retrieval_time:.2f}s")
                        with col2:
                            st.caption(f"⏱️ Generation: {generation_time:.2f}s")


st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>🤖 Powered by RAG Technology | 💾 Multiple Chat Rooms</div>", unsafe_allow_html=True)