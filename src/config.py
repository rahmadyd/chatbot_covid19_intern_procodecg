import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

ENV_MODE = "deploy"

FAISS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "faiss"))

INDEX_PATH = os.path.join(FAISS_DIR, "faiss_textcovid19.index")
TEXT_PATH  = os.path.join(FAISS_DIR, "faiss_textcovid19_texts.json")  

MODEL_CONFIG = {
    "embedding_model": "paraphrase-multilingual-mpnet-base-v2",
    "generation_model": "gemma:2b-instruct", 
    "retrieval_top_k": 15,
    "generation_top_k": 10,
    "language": "id",
    "device": "cpu",
    "temperature": 0.1,
    "top_p": 0.8,
    "score_threshold": 0.2
}

SYSTEM_PROMPT = """
Anda adalah asisten AI yang ahli dalam data COVID-19 Indonesia.

ATURAN MUTLAK:
1. JAWAB HANYA BERDASARKAN INFORMASI DI KONTEKS
2. JIKA TIDAK ADA INFORMASI YANG RELEVAN, katakan: "Maaf, informasi tidak ditemukan dalam dokumen sumber COVID-19 Indonesia."
3. JAWABAN HARUS SINGKAT, LANGSUNG, DAN FAKTUAL
4. JANGAN menambahkan informasi dari pengetahuan umum
5. Fokus pada dampak COVID-19 di Indonesia

FORMAT: Jawaban langsung dalam 1-3 kalimat.
"""

if __name__ == "__main__":
    print("PROJECT_ROOT:", PROJECT_ROOT)
    print("FAISS_DIR:", FAISS_DIR)
    print("INDEX_PATH:", INDEX_PATH) 
    print("INDEX_PATH exists:", os.path.exists(INDEX_PATH))
    print("TEXT_PATH:", TEXT_PATH)
    print("TEXT_PATH exists:", os.path.exists(TEXT_PATH))