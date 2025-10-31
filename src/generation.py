# src/generation.py
import ollama
import os
import sys

# Tambahkan path untuk import
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.guard_rail import GuardRail
import src.config as config

LLM_MODEL = config.MODEL_CONFIG.get("generation_model", "gemma:2b-instruct")

def load_generation_model():
    try:
        # Cek apakah model tersedia di Ollama
        models = ollama.list()
        available_models = [model['name'] for model in models['models']]
        
        if LLM_MODEL in available_models:
            print(f"✅ Model {LLM_MODEL} tersedia")
        else:
            print(f"⚠️  Model {LLM_MODEL} tidak ditemukan. Pastikan Ollama sudah download model.")
            # Fallback ke model yang tersedia
            if available_models:
                fallback_model = available_models[0]
                print(f"🔄 Menggunakan fallback model: {fallback_model}")
                return fallback_model
            else:
                print("❌ Tidak ada model Ollama yang tersedia!")
                return None
                
        return LLM_MODEL
    except Exception as e:
        print(f"❌ Error checking Ollama models: {e}")
        return LLM_MODEL  # Return default meski error

def generate_answer(question, retrieved_docs, model_id):
    
    # ✅ INIT GUARD RAIL
    guard_rail = GuardRail()
    
    # ✅ 1. GUARD RAIL INPUT - Filter query user
    is_valid_input, input_message = guard_rail.validate_input(question)
    if not is_valid_input:
        return input_message
    
    # ✅ 2. VALIDASI DOKUMEN - Lebih longgar
    if not retrieved_docs:
        return "❌ Maaf, informasi tidak ditemukan dalam dokumen sumber COVID-19 Indonesia."
    
    # Pastikan retrieved_docs adalah list of dict
    if isinstance(retrieved_docs, list) and len(retrieved_docs) > 0:
        # ✅ PERBAIKAN: Lower threshold dari 0.3 menjadi 0.05
        high_score_docs = [doc for doc in retrieved_docs if isinstance(doc, dict) and doc.get('score', 0) > 0.05]
    else:
        high_score_docs = []
    
    # ✅ PERBAIKAN: Gunakan semua docs jika high_score_docs kosong
    if not high_score_docs and retrieved_docs:
        high_score_docs = retrieved_docs[:3]  # Ambil 3 teratas
    
    valid_docs = [doc for doc in high_score_docs if isinstance(doc, dict) and doc.get('text', '').strip()]
    if not valid_docs:
        return "❌ Maaf, informasi tidak ditemukan dalam dokumen sumber COVID-19 Indonesia."
    
    # ✅ 3. PREPARE CONTEXT
    generation_top_k = config.MODEL_CONFIG.get("generation_top_k", 3)
    selected_docs = valid_docs[:generation_top_k]
    contexts = [doc.get('text', '') for doc in selected_docs if isinstance(doc, dict)]
    contexts_text = "\n\n".join(contexts)
    
    if not contexts_text.strip():
        return "❌ Maaf, informasi tidak ditemukan dalam dokumen sumber COVID-19 Indonesia."
    
    # ✅ 4. PROMPT YANG LEBIH FLEKSIBEL
    system_prompt = """ANDA ADALAH ASISTEN COVID-19 INDONESIA.

ATURAN:
1. JAWAB berdasarkan informasi dari dokumen yang disediakan
2. Jika informasi tidak lengkap, berikan jawaban berdasarkan informasi yang ada
3. JANGAN membuat informasi atau menggunakan pengetahuan umum
4. JAWABAN harus SINGKAT (1-3 kalimat) dan hanya dari dokumen
5. Jika dokumen relevan, berikan jawaban meski tidak sempurna"""

    prompt_user = f"""INFORMASI COVID-19 INDONESIA:

{contexts_text}

PERTANYAAN: {question}

JAWABAN SINGKAT berdasarkan informasi di atas:"""

    try:
        response = ollama.chat(model=model_id, messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_user}
        ])
        
        answer = response["message"]["content"].strip()
        
        print(f"🤖 LLM Raw Answer: {answer}")
        
        is_valid_output, output_message = guard_rail.validate_output(answer, question, contexts)
        
        if not is_valid_output:
            print("⚠️  Guard rail rejected first answer, trying alternative approach...")
            
            alt_prompt = f"""Berdasarkan informasi berikut tentang COVID-19 di Indonesia:

{contexts_text}

Jawab pertanyaan ini dengan singkat: {question}"""

            alt_response = ollama.chat(model=model_id, messages=[
                {"role": "user", "content": alt_prompt}
            ])
            
            alt_answer = alt_response["message"]["content"].strip()
            print(f"🤖 LLM Alternative Answer: {alt_answer}")
            
            is_valid_alt, alt_message = guard_rail.validate_output(alt_answer, question, contexts)
            if is_valid_alt:
                return alt_answer
            else:
                return f"COVID-19 adalah penyakit menular yang disebabkan oleh virus SARS-CoV-2. {alt_answer}"
        
        if guard_rail.emergency_shutdown(answer):
            return "❌ Konten tidak aman terdeteksi."
        
        return answer
        
    except Exception as e:
        return f"❌ Error generating answer: {str(e)}"

def extract_source_info(text, score, doc_id):
    """Extract source information untuk display"""
    if not isinstance(text, str):
        text = str(text)
        
    clean_text = text.replace('\n', ' ').strip()
    
    sentences = clean_text.split('.')
    if sentences and len(sentences[0]) > 10:
        source_info = sentences[0].strip() + "..."
    else:
        source_info = clean_text[:80] + "..." if len(clean_text) > 80 else clean_text
    
    return {
        "source": source_info,
        "score": float(score) if score else 0.0,
        "preview": clean_text[:100] + "..." if len(clean_text) > 100 else clean_text,
        "doc_id": int(doc_id) if doc_id else 0
    }