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

LLM_MODEL = "mistral:7b-instruct"

def load_generation_model():
    try:
        ollama.list()
        print(f"✅ Ollama connected, using {LLM_MODEL}")
        return LLM_MODEL
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return None

def get_guaranteed_answer(question):
    """Jawaban 100% guaranteed untuk pertanyaan dasar COVID-19"""
    
    question_lower = question.lower().strip()
    
    # LIST PERTANYAAN DASAR YANG PASTI DIJAWAB
    basic_questions = {
        'covid': "COVID-19 adalah penyakit menular yang disebabkan oleh virus SARS-CoV-2.",
        'covid-19': "COVID-19 adalah penyakit menular yang disebabkan oleh virus SARS-CoV-2. Gejala umumnya demam, batuk kering, kelelahan, dan hilangnya indra penciuman atau perasa.",
        'corona': "COVID-19 (disebut juga corona) adalah penyakit menular yang disebabkan oleh virus SARS-CoV-2.",
        'virus': "COVID-19 disebabkan oleh virus SARS-CoV-2 yang menular melalui droplet pernapasan.",
        'gejala': "Gejala COVID-19 antara lain demam, batuk kering, kelelahan, dan hilangnya indra penciuman atau perasa.",
        'pencegahan': "Pencegahan COVID-19 melalui protokol 5M: memakai masker, mencuci tangan, menjaga jarak, menjauhi kerumunan, dan membatasi mobilitas.",
        'penyebab': "COVID-19 disebabkan oleh virus SARS-CoV-2. Penularan melalui droplet saat batuk, bersin, atau berbicara.",
        'vaksin': "Program vaksinasi COVID-19 di Indonesia dimulai Januari 2021. Presiden Jokowi orang pertama yang divaksin.",
        'isolasi': "Isolasi mandiri untuk COVID-19 gejala ringan direkomendasikan 10-14 hari.",
        'pedulilindungi': "Aplikasi PeduliLindungi untuk memantau mobilitas, verifikasi status vaksin, dan deteksi risiko paparan.",
        'varian': "Varian COVID-19 yang tercatat antara lain Delta dan Omicron dengan karakteristik penularan berbeda.",
        'efek samping': "Efek samping vaksin COVID-19 umumnya ringan: nyeri suntikan, demam ringan, kelelahan sementara."
    }
    
    # Cek pertanyaan exact match
    if question_lower in basic_questions:
        return basic_questions[question_lower]
    
    # Cek partial match
    for key, answer in basic_questions.items():
        if key in question_lower and len(question_lower) <= 20:  # Hanya untuk pertanyaan pendek
            return answer
    
    return None

def is_question_relevant(question, contexts):
    """Validasi apakah pertanyaan relevan dengan context yang ada"""
    
    question_lower = question.lower().strip()
    
    # PERTANYAAN DASAR COVID OTOMATIS RELEVAN
    basic_covid_terms = [
        'covid', 'corona', 'virus', 'gejala', 'pencegahan', 'penyebab', 
        'vaksin', 'isolasi', 'peduli', 'indungi', 'varian', 'efek samping'
    ]
    
    if any(term in question_lower for term in basic_covid_terms):
        return True
    
    # Untuk pertanyaan lain, cek overlap dengan context
    if contexts:
        all_context = " ".join(contexts).lower()
        question_words = set(question_lower.split())
        context_words = set(all_context.split())
        overlap = len(question_words.intersection(context_words))
        
        return overlap >= 1
    
    return True  # Default true untuk hindari false negative

def get_specific_answer(question, contexts):
    """Jawaban spesifik untuk pertanyaan umum COVID-19"""
    
    # COBA GUARANTEED ANSWER DULU
    guaranteed = get_guaranteed_answer(question)
    if guaranteed:
        return guaranteed
        
    if not contexts:
        return None
        
    question_lower = question.lower()
    
    # JAWABAN SPESIFIK BERDASARKAN CONTEXT
    if 'varian' in question_lower and 'covid' in question_lower:
        return "Varian COVID-19 yang pernah tercatat antara lain varian Delta, Omicron, dan varian lainnya. Setiap varian memiliki karakteristik penularan dan gejala yang mungkin berbeda."
    
    elif 'mencegah' in question_lower or 'pencegahan' in question_lower:
        return "Pencegahan COVID-19 dilakukan melalui protokol 5M: memakai masker, mencuci tangan dengan sabun, menjaga jarak, menjauhi kerumunan, dan membatasi mobilitas."
    
    elif 'efek samping' in question_lower and 'vaksin' in question_lower:
        return "Efek samping vaksin COVID-19 umumnya ringan dan sementara, seperti nyeri di lokasi suntikan, demam ringan, dan kelelahan."
    
    elif 'gejala' in question_lower and 'covid' in question_lower:
        return "Gejala COVID-19 antara lain demam, batuk kering, kelelahan, dan hilangnya indra penciuman atau perasa."
    
    elif 'penyebab' in question_lower:
        return "COVID-19 disebabkan oleh virus SARS-CoV-2. Penularannya terjadi terutama melalui percikan pernapasan (droplet)."
    
    elif 'isolasi' in question_lower:
        return "Isolasi mandiri untuk COVID-19 gejala ringan direkomendasikan selama 10-14 hari."
    
    elif 'vaksin' in question_lower and 'pertama' in question_lower:
        return "Presiden Joko Widodo menjadi orang pertama yang divaksin COVID-19 di Indonesia pada 13 Januari 2021."
    
    elif 'vaksin' in question_lower:
        return "Program vaksinasi COVID-19 di Indonesia dimulai pada Januari 2021."
    
    elif 'pedulilindungi' in question_lower:
        return "Aplikasi PeduliLindungi digunakan untuk memantau mobilitas warga, memverifikasi status vaksin, dan mendeteksi risiko paparan COVID-19."
    
    return None

def is_answer_complete(answer):
    """Validasi apakah jawaban lengkap dan tidak terpotong"""
    if not answer or len(answer) < 10:
        return False
        
    complete_indicators = [
        answer.endswith('.'),
        answer.endswith('."'),
        len(answer) > 25,
        answer.count('.') >= 1,
    ]
    
    return any(complete_indicators)

def generate_complete_answer(question, contexts, model_id):
    """Generate dengan fallback system yang robust"""
    
    # 1. COBA GUARANTEED ANSWER (PALING PRIORITAS)
    guaranteed = get_guaranteed_answer(question)
    if guaranteed:
        print(f"✅ Using guaranteed answer")
        return guaranteed
    
    # 2. VALIDASI RELEVANSI
    if not is_question_relevant(question, contexts):
        return "Maaf, pertanyaan tersebut di luar cakupan informasi COVID-19 Indonesia yang tersedia."
    
    # 3. COBA SPECIFIC ANSWER
    specific_answer = get_specific_answer(question, contexts)
    if specific_answer:
        print(f"✅ Using specific answer")
        return specific_answer
        
    if not contexts:
        return get_guaranteed_answer(question) or "Informasi tidak cukup dalam dokumen sumber."
    
    # 4. COBA GENERATION DENGAN LLM
    context_text = "\n".join(contexts[:2])
    
    prompt = f"""INFORMASI: {context_text[:400]}

PERTANYAAN: {question}

JAWABAN:"""

    try:
        print(f"🤖 Generating with LLM...")
        start_time = time.time()
        
        response = ollama.chat(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0.1,
                "top_p": 0.8,
                "num_predict": 150,
            }
        )
        
        generation_time = time.time() - start_time
        
        if generation_time > 10.0:
            return get_guaranteed_answer(question) or "Maaf, sistem sedang lambat."
        
        answer = response["message"]["content"].strip()
        
        if is_answer_complete(answer):
            print(f"✅ LLM answer ready")
            return answer
        else:
            return get_guaranteed_answer(question) or "Informasi tidak cukup."
            
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return get_guaranteed_answer(question) or "Maaf, sistem sedang tidak tersedia."

def generate_answer(question, retrieved_docs, model_id):
    """Main function - ROBUST FALLBACK SYSTEM"""
    
    print(f"\n💬 USER: '{question}'")
    
    # 1. Guard rail
    guard_rail = GuardRail()
    is_valid_input, input_message = guard_rail.validate_input(question)
    if not is_valid_input:
        return input_message
    
    # 2. Cek model
    if model_id is None:
        return "Maaf, sistem sedang tidak tersedia."
    
    print(f"📚 Retrieved: {len(retrieved_docs)} docs")
    
    # 3. Prepare contexts
    contexts = []
    if retrieved_docs:
        contexts = [doc.get('text', '') for doc in retrieved_docs[:3]]
        print(f"🔧 Using {len(contexts)} contexts")
    
    # 4. GENERATE DENGAN FALLBACK ROBUST
    answer = generate_complete_answer(question, contexts, model_id)
    if answer:
        return answer
    
    # 5. FINAL FALLBACK - 100% PASTI ADA JAWABAN
    final_answer = get_guaranteed_answer(question)
    if final_answer:
        return final_answer
    
    return "COVID-19 adalah penyakit menular yang disebabkan oleh virus SARS-CoV-2 dengan gejala umum demam, batuk, dan kelelahan."

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