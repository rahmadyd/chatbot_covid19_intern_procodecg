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
    "top_p": 0.7,
    "score_threshold": 0.1   
}

SYSTEM_PROMPT = """
Anda adalah asisten AI untuk COVID-19 Indonesia.

JAWAB BERDASARKAN INFORMASI DI KONTEKS SAJA.
JAWAB SINGKAT dan LANGSUNG.
JANGAN tambahkan informasi dari pengetahuan umum.
"""

if __name__ == "__main__":
    print("PROJECT_ROOT:", PROJECT_ROOT)
    print("FAISS_DIR:", FAISS_DIR)
    print("INDEX_PATH:", INDEX_PATH) 
    print("INDEX_PATH exists:", os.path.exists(INDEX_PATH))
    print("TEXT_PATH:", TEXT_PATH)
    print("TEXT_PATH exists:", os.path.exists(TEXT_PATH))