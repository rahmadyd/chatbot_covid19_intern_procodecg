#COFIG FILE FOR DEPLOY 
import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ENV_MODE = "deploy"

INDEX_PATH = "./vectorstore/last_covid19_faiss.index"
TEXT_PATH  = "./vectorstore/last_covid19_faiss_texts.json"

MODEL_CONFIG = {
    "embedding_model": "intfloat/multilingual-e5-base",
    "generation_model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "top_k": 3,
    "language": "id",
    "device": "cpu"
}

SYSTEM_PROMPT = "Chatbot yang hanya membahas tentang COVID-19 di Indonesia"

if __name__ == "__main__":