# src/guard_rail.py - COMPLETE SECURITY VERSION
import re
from typing import Dict, List, Tuple

class GuardRail:
    def __init__(self):
        self.covid_keywords = [
            # COVID & Virus
            'covid', 'corona', 'virus', 'pandemi', 'sars-cov-2', 'varian',
            
            # Gejala & Kesehatan
            'gejala', 'demam', 'batuk', 'kelelahan', 'penciuman', 'perasa', 'sesak napas',
            'isolasi', 'karantina', 'kesehatan', 'medis', 'rumah sakit',
            
            # Vaksinasi - DIPERLUAS
            'vaksin', 'vaksinasi', 'sinovac', 'astrazeneca', 'moderna', 'pfizer', 
            'booster', 'dosis', 'sertifikat', 'presiden', 'jokowi', 'orang pertama',
            'suntik', 'imunisasi', 'vaksinasi', 'divaksin', 'joko widodo',
            
            # Pencegahan & Protokol
            'pencegahan', 'cegah', 'protokol', 'masker', 'cuci tangan', 'jarak',
            'kerumunan', 'mobilitas', '5m',
            
            # Kebijakan & Program
            'psbb', 'ppkm', 'pembatasan', 'kebijakan', 'program',
            
            # Aplikasi & Teknologi
            'pedulilindungi', 'aplikasi', 'tracking',
            
            # Bantuan & Ekonomi
            'bantuan', 'blt', 'prakerja', 'umkm', 'usaha', 'ekonomi',
            
            # Data & Statistik
            'data', 'statistik', 'kasus', 'positif', 'sembuh', 'meninggal',
            
            # KATA UMUM YANG SERING DITANYAKAN - TAMBAHAN
            'siapa', 'apa', 'kapan', 'berapa', 'bagaimana', 'dimana',
            'pertama', 'orang', 'presiden', 'menteri', 'dokter', 'perawat',
            'benar', 'apakah', 'siapakah'
        ]
        
        self.rejected_topics = [
            # Makanan & Minuman
            'makanan', 'minuman', 'restoran', 'warung', 'kue', 'cheesecake', 'martabak',
            'resep', 'masak', 'memasak', 'kuliner',
            
            # Hiburan
            'musik', 'lagu', 'artis', 'band', 'snsd', 'bts', 'blackpink', 'hearts',
            'film', 'drama', 'sinetron', 'netflix', 'youtube', 'tiktok',
            'game', 'mobile legend', 'free fire', 'pubg',
            
            # Olahraga
            'olahraga', 'sepak bola', 'bulutangkis', 'tenis', 'basket',
            
            # Politik & Sosial
            'politik', 'pemilu', 'pilkada', 'partai',
            'ras', 'suku', 'agama', 'etnis',
            
            # Relationship
            'cinta', 'love', 'pacaran', 'relationship', 'i love you', 'romantis',
        ]
        
        self.dangerous_keywords = [
            'bunuh diri', 'melukai', 'bunuh', 'racun', 'bom', 'senjata',
            'kekerasan', 'teror', 'extrem', 'radikal'
        ]
        
        self.security_blocked_keywords = [
            'meretas', 'hack', 'crack', 'bypass', 'exploit', 'virus', 'malware',
            'serangan', 'attack', 'injeksi', 'injection', 'sql injection',
            'backdoor', 'remote access', 'brute force', 'password', 'login',
            'security bug', 'kerentanan', 'vulnerability', 'zero day',
            'deface', 'ddos', 'phishing', 'social engineering',
            'keylogger', 'trojan', 'ransomware', 'spyware'
        ]

    def validate_input(self, query: str) -> Tuple[bool, str]:
        """Guard rail untuk input query dari user - DITAMBAH SECURITY"""
        query_lower = query.lower()
        
        # 1. Cek kata berbahaya - PRIORITAS TERTINGGI
        for danger in self.dangerous_keywords:
            if danger in query_lower:
                return False, "❌ Pertanyaan mengandung konten yang tidak aman."
        
        for security_word in self.security_blocked_keywords:
            if security_word in query_lower:
                return False, "❌ Saya tidak dapat membantu dengan pertanyaan terkait keamanan siber atau peretasan."
        
        # 2. SPECIAL CASE: Pertanyaan tentang "siapa" otomatis diterima jika ada konteks COVID
        if 'siapa' in query_lower and any(kw in query_lower for kw in ['vaksin', 'covid', 'corona', 'presiden', 'orang pertama']):
            return True, "OK"
            
        # 3. SPECIAL CASE: Pertanyaan tentang "orang pertama" otomatis diterima
        if 'orang pertama' in query_lower or 'pertama' in query_lower and 'vaksin' in query_lower:
            return True, "OK"

        # 4. SPECIAL CASE: Pertanyaan "apakah benar" tentang COVID
        if 'apakah' in query_lower and 'benar' in query_lower and any(kw in query_lower for kw in ['vaksin', 'covid', 'jokowi']):
            return True, "OK"
        
        # 5. Cek topik ditolak - HANYA YANG BENAR-BENAR TIDAK RELEVAN
        for topic in self.rejected_topics:
            if topic in query_lower:
                # KECUALI jika juga mengandung kata COVID
                if not any(covid_kw in query_lower for covid_kw in ['covid', 'corona', 'vaksin', 'pandemi']):
                    return False, f"❌ Maaf, saya hanya dapat menjawab pertanyaan tentang COVID-19 di Indonesia."
        
        # 6. Cek apakah query tentang COVID - LEBIH FLEKSIBEL
        is_covid_related = any(keyword in query_lower for keyword in self.covid_keywords)
        
        if not is_covid_related:
            return False, "❌ Maaf, saya hanya dapat menjawab pertanyaan tentang COVID-19 di Indonesia."
        
        return True, "OK"

    def validate_output(self, answer: str, question: str, contexts: List[str]) -> Tuple[bool, str]:
        """Guard rail untuk output dari LLM - DITAMBAH SECURITY"""
        answer_lower = answer.lower()
        question_lower = question.lower()
        
        # 1. Biarkan rejection phrases pass
        rejection_phrases = ['maaf', 'tidak tahu', 'tidak bisa', 'tidak ditemukan']
        if any(phrase in answer_lower for phrase in rejection_phrases):
            return True, "OK"
        
        security_indicators = [
            'password', 'login', 'akses', 'remote', 'bug', 'kerentanan',
            'exploit', 'bypass', 'crack', 'hack'
        ]
        
        if any(sec_word in question_lower for sec_word in self.security_blocked_keywords):
            if any(sec_indicator in answer_lower for sec_indicator in security_indicators):
                return False, "❌ Jawaban mengandung informasi keamanan yang tidak sesuai."
        
        # 2. Cek topik ditolak dalam jawaban
        for topic in self.rejected_topics:
            if topic in answer_lower:
                # KECUALI jika itu bagian dari konteks COVID
                if not any(covid_kw in answer_lower for covid_kw in ['covid', 'corona', 'vaksin']):
                    return False, "❌ Maaf, informasi tidak ditemukan dalam dokumen sumber COVID-19 Indonesia."
        
        # 3. Cek kata berbahaya dalam jawaban
        for danger in self.dangerous_keywords:
            if danger in answer_lower:
                return False, "❌ Jawaban mengandung konten yang tidak aman."
        
        return True, "OK"

    def emergency_shutdown(self, answer: str) -> bool:
        """Emergency shutdown untuk jawaban yang sangat berbahaya"""
        emergency_phrases = [
            'bunuh diri', 'bunuh dirimu', 'racun', 'bom', 'senjata api',
            'kekerasan seksual', 'perkosaan', 'cara hack', 'cara meretas',
            'bypass security', 'exploit bug', 'sql injection'
        ]
        
        answer_lower = answer.lower()
        return any(phrase in answer_lower for phrase in emergency_phrases)