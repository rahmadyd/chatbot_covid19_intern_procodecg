# 🦠 COVID-19 Chatbot (True RAG Architecture)

Chatbot AI interaktif yang dirancang untuk memberikan informasi akurat dan faktual mengenai penanganan COVID-19 di Indonesia menggunakan teknologi **Retrieval-Augmented Generation (RAG)** murni.

Dibangun khusus agar berjalan sangat ringan, responsif, dan optimal merespons instruksi kompleks dengan menggunakan **Mistral 7B-Instruct** LLM secara lokal via Ollama, sangat cocok untuk kapabilitas RAM dan VRAM menengah.

---

## ✨ Fitur Unggulan

- **True RAG Pipeline**: Chatbot 100% menarik pengetahuan berlandaskan dokumen FAISS secara dinamis tanpa mengandalkan *hardcoded fallback*.
- **Semantic Vector Search**: Menggunakan embedding `paraphrase-multilingual-mpnet-base-v2` untuk mencari kesamaan makna antara pertanyaan dan dokumen rujukan tanpa pencocokan kata kaku (*word overlap*).
- **Multi Chat Rooms & History Persistence**: Mendukung pembuatan banyak ruang obrolan (*chat rooms*), ubah nama, hapus chat, serta menyimpan riwayat percakapan secara otomatis ke `data/chat_rooms.json`.
- **Transparansi Sumber Referensi**: Setiap jawaban dilengkapi dengan rincian sumber referensi, tingkat relevansi (*similarity score*), dan cuplikan teks dokumen yang digunakan.
- **Robust Guardrail**: Saringan keamanan otomatis di [src/guard_rail.py](file:///d:/chatbot_covid19_intern_procodecg/src/guard_rail.py) yang melindungi sistem dari *prompt injection*, topik di luar konteks COVID-19, serta kata kunci berbahaya.
- **Retrieval Debugger**: Fitur interaktif untuk menganalisis dan menguji skor relevansi dokumen FAISS secara transparan.
- **Lightweight & Efisien**: Berjalan murni dengan Python, FAISS, dan Ollama tanpa *framework bloatware* berlebih.

---

## 🛠️ Tech Stack

* **Language**: Python 3.x
* **Vector DB**: FAISS (Facebook AI Similarity Search)
* **Embeddings**: `paraphrase-multilingual-mpnet-base-v2` (via `sentence-transformers`)
* **Local LLM**: Mistral 7B-Instruct (7 Billion Parameters) via **Ollama**
* **Frontend UI**: Streamlit (Multi-page app)

---

## 📂 Struktur Repository

```text
chatbot_covid19_intern_procodecg/
├── data/                       # Data mentah, hasil chunking, & riwayat chat
│   ├── chat_rooms.json         # Data riwayat percakapan chat rooms
│   └── chunks.json             # Dokumen teks yang sudah di-chunk
├── faiss/                      # Index & metadata FAISS Vector Store
│   ├── faiss_textcovid19.index # File index FAISS
│   └── faiss_textcovid19_texts.json # Metadata/teks dokumen FAISS
├── notebooks/                  # Notebook eksperimen & pipeline data
│   ├── 01_data_cleaning.ipynb
│   ├── 02_text_chunking.ipynb
│   ├── 03_embedding_test.ipynb
│   ├── 04_Indexing_faiss.ipynb
│   └── 05_retrieval_demo.ipynb
├── src/                        # Logic utama RAG Backend
│   ├── config.py               # Konfigurasi model, path, & prompt
│   ├── generation.py           # Pipeline pemanggilan LLM Ollama
│   ├── guard_rail.py           # Validasi & pengaman input/output
│   └── retriever.py            # Pencarian vektor FAISS
├── streamlit_app/              # Antarmuka Pengguna (Frontend)
│   ├── app.py                  # Entrypoint / Halaman Utama
│   └── pages/                  # Halaman navigasi (Chat, Debug, Config, Cache)
│       ├── 01_chat.py          # Halaman Chatbot Utama
│       ├── 02_retrieval_debug.py # Halaman Debugger Retrieval
│       ├── 03_config_tester.py # Halaman Pengujian Konfigurasi
│       └── 04_clear_cache.py   # Halaman Pembersihan Cache
├── lampiran/                   # Diagram arsitektur & screenshot aplikasi
├── requirements.txt            # Package dependencies
└── README.md                   # Dokumentasi proyek
```

---

## 🚀 Panduan Instalasi & Penggunaan

### 1. Persiapan Repository
```bash
git clone https://github.com/rahmadyd/chatbot_covid19_intern_procodecg.git
cd chatbot_covid19_intern_procodecg
```

### 2. Install Dependencies
Disarankan menggunakan virtual environment:
```bash
pip install -r requirements.txt
```

### 3. Setup Ollama & Tarik Model AI
Pastikan aplikasi [Ollama](https://ollama.com/) sudah terinstall dan berjalan di latar belakang (background). Buka terminal / CMD lalu jalankan:
```bash
ollama pull mistral:7b-instruct
```
*(Atau `ollama pull mistral` untuk tag standar Mistral 7B-Instruct).*

### 4. Jalankan Aplikasi Web Streamlit
```bash
streamlit run streamlit_app/app.py
```
Aplikasi akan otomatis terbuka di browser di `http://localhost:8501`.

---

## ⚙️ Penyesuaian & Konfigurasi

Anda dapat menyesuaikan parameter sistem pada file `src/config.py`:
- `generation_model` : Mengatur model LLM Ollama yang digunakan (default: `mistral:7b-instruct`).
- `embedding_model` : Model embedding SentenceTransformer (default: `paraphrase-multilingual-mpnet-base-v2`).
- `score_threshold` : Ambang batas kemiripan dokumen FAISS.
- `temperature` & `top_p` : Mengatur tingkat kreativitas dan keberagaman jawaban LLM.

---

## 📜 Lisensi & Acknowledgments
- Dikembangkan dalam rangka program magang di **ProcodeCG**.
- Menggunakan teknologi Semantic Search murni berbasis FAISS, Sentence Transformers, dan local LLM Ollama.