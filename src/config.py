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
    "device": "cpu",
    "temperature" : 0.7,
    "top_p": 0.9
}

SYSTEM_PROMPT = "Chatbot yang hanya membahas tentang COVID-19 di Indonesia"

if __name__ == "__main__":
    print("BASE_DIR:", BASE_DIR)
    print("INDEX_PATH:", INDEX_PATH) 
    print("TEXT_PATH exists:", os.path.exists(TEXT_PATH))