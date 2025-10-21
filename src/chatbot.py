# src/generation.py
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from src.config import MODEL_CONFIG, SYSTEM_PROMPT as PROMPT  # sesuaikan import jika perlu

# ==============================
# 1️⃣ LOAD LLM / PIPELINE
# ==============================
def load_generation_model():
    """
    TODO: load model & tokenizer atau pipeline sesuai MODEL_CONFIG["generation_model"].
    Harus return object yang bisa dipanggil untuk generate text.
    """
    model_use = MODEL_CONFIG["generation_model"]
    device = MODEL_CONFIG["device"]
    
    tokenizer = AutoTokenizer.from_pretrained(model_use)
    model = AutoModelForCausalLM.from_pretrained(model_use)
    
    generator = pipeline(
        "text2text-generation",
        model = model,
        tokenizer = tokenizer,
        device=0 if device == "cuda" else -1
    )
    
    return generator 
    

# ==============================
# 2️⃣ AUGMENTATION + GENERATION
# ==============================
def generate_answer(query, contexts, generator, system_prompt=PROMPT, max_tokens=300):
    """
    - contexts: list of strings from retriever
    - generator: object returned by load_generation_model()
    - system_prompt: SYSTEM_PROMPT (opsional)
    Return: generated answer (string)
    """
    # TODO:
    # 1. gabungkan contexts jadi 1 string (augmentasi)
    # 2. susun prompt final (sertakan system_prompt jika ada)
    # 3. panggil generator untuk menghasilkan jawaban
    # 4. kembalikan jawaban sebagai string
    
    augmented_context =  "\n".join(contexts)
    
    final_prompt = f"""
    {system_prompt}

    Konteks:
    {augmented_context}

    Pertanyaan: {query}
    Jawaban:
    """

    print("Token lenght of prompt is:",len(generator.tokenizer(final_prompt)["input_ids"]))
    
    output = generator(
        final_prompt, 
        max_new_tokens = max_tokens, 
        do_sample=True,
        top_k = MODEL_CONFIG["top_k"],
        top_p = MODEL_CONFIG["top_p"],
        temperature = MODEL_CONFIG["temperature"],
        truncation=True,
        eos_token_id=generator.tokenizer.eos_token_id
    )
    
    raw_text_output = output[0]["generated_text"]
    
    if "Jawaban:" in raw_text_output:
        cleaned_answer_output = raw_text_output.split("Jawaban:")[0].strip()
    else:
        cleaned_answer_output = raw_text_output.strip()
    
    return cleaned_answer_output
                                
    

# ==============================
# 3️⃣ DEBUG / LOCAL TESTING
# ==============================
if __name__ == "__main__":
    # TODO: load generator, panggil generate_answer() dengan contoh contexts & query, print hasilnya
    
    # Pipeline RAG (query → retrieve → LLM → jawaban)
    generator = load_generation_model()
    
    query = [
        "Apa saja gejala umum COVID-19?",
        "Apakah gejala bisa ringan hingga berat?",
        "Apakah ada pasien yang mengalami nyeri tenggorokan?"
    ]
    
    contexts = [
        "Gejala umum COVID-19 meliputi demam, batuk kering, dan kelelahan.",
        "Beberapa pasien juga mengalami nyeri tenggorokan, diare, dan kehilangan indera penciuman.",
        "Gejala bisa ringan hingga berat, tergantung kondisi tubuh dan usia pasien."
    ]
    
    for i, q in enumerate(query,1):
        answer = generate_answer(q, contexts, generator, max_tokens=150)
        print(f"\n❓ Pertanyaan {i}: {q}")
        print(f"\n📝 Jawaban: {answer}")
        print("-" * 60)