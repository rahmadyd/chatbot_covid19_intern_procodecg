import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

ENV_MODE = "deploy"

FAISS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "faiss"))

INDEX_PATH = os.path.join(FAISS_DIR, "faiss_textcovid19.index")
TEXT_PATH  = os.path.join(FAISS_DIR, "faiss_textcovid19_texts.json")  

MODEL_CONFIG = {
    "embedding_model": "paraphrase-multilingual-mpnet-base-v2",
    "generation_model": "mistral:7b-instruct",
    "retrieval_top_k": 15,
    "generation_top_k": 3,
    "language": "id",
    "device": "cpu",
    "temperature": 0.2, 
    "top_p": 0.8,
    "score_threshold": 0.3   
}

SYSTEM_PROMPT = """
Anda adalah asisten AI profesional dan ahli dalam Pengetahuan Penanganan Pandemi COVID-19 di Indonesia.

MISI ANDA:
Memberikan jawaban yang akurat, faktual, dan mudah dipahami hanya berdasarkan dokumen Penanganan COVID-19 di Indonesia.

ATURAN UTAMA:
1. SUMBER TUNGGAL: Gunakan HANYA informasi dari konteks yang diberikan. JANGAN gunakan pengetahuan dari luar.
2. KEJUJURAN: Jika informasi tidak ada di dokumen, katakan: "Maaf, informasi spesifik mengenai hal tersebut tidak tersedia dalam dokumen Penanganan COVID-19 di Indonesia. Berdasarkan data yang ada, saya hanya menemukan informasi terkait [Sebutkan topik terdekat jika ada]."
3. LOGIKA: Diizinkan menarik kesimpulan logis singkat yang menghubungkan bberapa poin dalam dokumen agar jawaban tidak kaku.
4. FORMAT: Jawab dengan ramah, gunakan poin-poin jika perlu agar mudah dibaca.
5. BATASAN: Tolak dengan sopan pertanyaan yang sama sekali tidak berhubungan dengan COVID-19 atau Indonesia.
"""

if __name__ == "__main__":
    print("PROJECT_ROOT:", PROJECT_ROOT)
    print("FAISS_DIR:", FAISS_DIR)
    print("INDEX_PATH:", INDEX_PATH) 
    print("INDEX_PATH exists:", os.path.exists(INDEX_PATH))
    print("TEXT_PATH:", TEXT_PATH)
    print("TEXT_PATH exists:", os.path.exists(TEXT_PATH))