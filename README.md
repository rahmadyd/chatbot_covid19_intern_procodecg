# 🦠 COVID-19 Chatbot (True RAG Architecture)

Chatbot AI interaktif yang dirancang untuk memberikan informasi akurat tentang COVID-19 di Indonesia, menggunakan teknologi **Retrieval-Augmented Generation (RAG)**. 

Dibangun khusus agar berjalan sangat ringan, responsif, dan optimal merespons instruksi kompleks dengan menggunakan **Qwen2.5 3B** LLM secara lokal, sangat cocok untuk kapabilitas RAM dan VRAM menangah (eg: 4GB VRAM).

---

## ✨ Fitur Unggulan

- **True RAG Pipeline**: Chatbot 100% menarik pengetahuan berlandaskan dokumen FAISS (tidak pakai hardcoded fallback).
- **Semantic Vector Search**: Mencari kesamaan makna antara pertanyaan dan dokumen rujukan tanpa mengandalkan pencocokan kata kaku (word overlap).
- **Lightweight & Efisien**: Dependencies super ramping (tidak butuh Langchain/Bloatware), respons sekejap.
- **Advanced Local LLM**: Didukung oleh kecerdasan *Qwen2.5 3B* via Ollama yang sangat natural untuk tata bahasa Indonesia.
- **Robust Guardrail**: Perlindungan otomatis, aman dari prompt injection/security threats, dan dioptimasi khusus untuk tidak memblokir keyword "virus corona".

---

## 🛠️ Tech Stack

* **Backend**: Python 3.x
* **Vector DB**: FAISS (Facebook AI Similarity Search)
* **Embeddings**: `paraphrase-multilingual-mpnet-base-v2`
* **Local LLM**: Qwen2.5 (3 Billion Parameters) via **Ollama**
* **Frontend UI**: Streamlit

---

## 🚀 Panduan Instalasi (Standard)

Ikuti langkah-langkah di bawah ini untuk menjalankan chatbot secara lokal.

### 1. Persiapan Repository
```bash
git clone https://github.com/rahmadyd/chatbot_covid19_intern_procodecg.git
cd chatbot_covid19_intern_procodecg
```

### 2. Install Dependencies
Pastikan kamu menggunakan virtual environment (opsional namun disarankan).
```bash
pip install -r requirements.txt
```

### 3. Setup Ollama & Tarik Model AI
Pastikan aplikasi [Ollama](https://ollama.com/) sudah terinstall dan berjalan di background laptop kamu. Lalu buka terminal/CMD dan jalankan:
```bash
ollama pull qwen2.5:3b
```
*(Model ini besarnya hanya sekitar ~1.9 GB dan sangat bersahabat untuk VRAM 4GB).*

### 4. Jalankan Aplikasi Web
```bash
streamlit run streamlit_app/app.py
```

Aplikasi otomatis akan terbuka di browser kamu (biasanya di `http://localhost:8501`).

---

## ⚙️ Penyesuaian & Konfigurasi Ekstra
Kamu dapat memodifikasi batas kreativitas AI dan limit pencarian dokumen melalui file `src/config.py`:
- `generation_model` : Mengatur model ollama apa yang ingin di eksekusi.
- `score_threshold` : (Default `0.3`) Mengatur seberapa longgar/ketat kemiripan makna dokumen rujukan FAISS.
- `num_predict` : Ekstra limit max panjang karakter balasan (di file `generation.py`).

---

## 📜 Lisensi & Acknowledgments
- Dikembangkan dalam rangka program magang di **ProcodeCG**.
- Menggunakan teknologi Semantic Search murni berbasis FAISS dan Sentence Transformers.