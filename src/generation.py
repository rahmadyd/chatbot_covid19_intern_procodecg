import ollama
import os
import sys
import time
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.guard_rail import GuardRail
import src.config as config

LLM_MODEL = config.MODEL_CONFIG.get("generation_model", "gemma:2b-instruct")

def load_generation_model():
    try:
        ollama.list()
        print(f"✅ Ollama connected, using {LLM_MODEL}")
        return LLM_MODEL
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return None

def generate_complete_answer(question, contexts, model_id):
    """Generate dengan LLM murni berdasarkan konteks RAG"""
    
    if not contexts:
        return "Maaf, informasi spesifik mengenai hal tersebut tidak tersedia dalam dokumen Penanganan COVID-19 di Indonesia."
    
    # Ambil lebih banyak context jika tersedia untuk akurasi
    context_text = "\n---\n".join(contexts[:3])
    
    # Prompt yang lebih tertata
    prompt = f"""TUGAS: Jawab pertanyaan di bawah berdasarkan DOKUMEN REFERENSI.
    
DOKUMEN REFERENSI:
{context_text}

PERTANYAAN: {question}

JAWABAN:"""

    try:
        print(f"🤖 Generating with model: {model_id}...")
        start_time = time.time()
        
        response = ollama.chat(
            model=model_id,
            messages=[
                {"role": "system", "content": config.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": config.MODEL_CONFIG.get("temperature", 0.2),
                "top_p": config.MODEL_CONFIG.get("top_p", 0.8),
                "num_predict": 512, # Ditingkatkan agar LLM bisa merespons lebih panjang
            }
        )
        
        generation_time = time.time() - start_time
        print(f"⏱️ Generation finished in {generation_time:.2f}s")
        
        answer = response["message"]["content"].strip()
        
        # Bersihkan jawaban dari tag atau prefix yang sering muncul di model kecil
        answer = re.sub(r"^(JAWABAN:|Answer:|Jawaban:)", "", answer).strip()
        
        return answer
            
    except Exception as e:
        print(f"❌ CRITICAL Generation error: {str(e)}")
        return "Maaf, layanan chatbot sedang mengalami gangguan teknis. Silakan coba beberapa saat lagi."

def generate_answer(question, retrieved_docs, model_id):
    """Main function - SUPREME ROBUST SYSTEM"""
    
    # Pastikan model_id benar
    if not model_id:
        from src import config
        model_id = config.MODEL_CONFIG.get("generation_model", "qwen2.5:3b")

    print(f"\n💬 USER: '{question}'")
    
    # 1. Guard rail
    guard_rail = GuardRail()
    is_valid_input, input_message = guard_rail.validate_input(question)
    if not is_valid_input:
        print(f"🛡️ GuardRail blocked: {input_message}")
        return input_message
    
    # 2. Cek Ollama Connection
    try:
        ollama.list()
    except:
        return "⚠️ Server AI (Ollama) tidak merespon. Pastikan aplikasi Ollama sudah terbuka di background."
    
    print(f"📚 Retrieved: {len(retrieved_docs)} docs")
    
    # 3. Prepare contexts
    contexts = []
    if retrieved_docs:
        contexts = [doc.get('text', '') for doc in retrieved_docs]
        print(f"🔧 Using {len(contexts[:3])} primary contexts")
    
    # 4. GENERATE DENGAN FALLBACK ROBUST
    return generate_complete_answer(question, contexts, model_id)

def extract_source_info(text, score, doc_id):
    """Extract source information"""
    if not isinstance(text, str):
        text = str(text)
        
    clean_text = text.replace('\n', ' ').strip()
    
    sentences = clean_text.split('.')
    source_info = ""
    for sentence in sentences:
        if len(sentence.strip()) > 20:
            source_info = sentence.strip() + "..."
            break
    
    if not source_info:
        source_info = clean_text[:80] + "..." if len(clean_text) > 80 else clean_text
    
    return {
        "source": source_info,
        "score": float(score) if score else 0.0,
        "preview": clean_text[:100] + "..." if len(clean_text) > 100 else clean_text,
        "doc_id": int(doc_id) if doc_id else 0
    }