# src/guard_rail.py
import re
from typing import Dict, List, Tuple

class GuardRail:
    def __init__(self):
        # ✅ DAFTAR KATA KUNCI COVID YANG DITERIMA
        self.covid_keywords = [
            'covid', 'corona', 'virus', 'pandemi', 'vaksin', 'gejala',
            'indonesia', 'kasus', 'penularan', 'isolasi', 'protokol',
            'infodemi', 'varian', 'sars-cov-2', 'stres', 'mental',
            'psikologis', 'dampak', 'kesehatan jiwa', 'masker',
            'cuci tangan', 'jarak', 'social distancing', 'lockdown',
            'ppkm', 'otomda', 'kasus aktif', 'positif', 'sembuh', 'meninggal',
            'rs rujukan', 'nakes', 'tenaga kesehatan', 'oksigen', 'ventilator',
            'teledokter', 'telemedisin', 'tatap muka', 'pembatasan',
            'klaster', 'penyebaran', 'mutasi', 'booster', 'dosis',
            'efikasi', 'efek samping', 'komorbid', 'penyakit bawaan',
            'imunisasi', 'herd immunity', 'kekebalan kelompok', 'antibodi',
            'antigen', 'pcr', 'swab', 'rapid test', 'test mandiri',
            '5m', 'memakai masker', 'mencuci tangan', 'menjaga jarak',
            'menjauhi kerumunan', 'membatasi mobilitas',
            'wfh', 'work from home', 'pembelajaran jarak jauh', 'pjj',
            'new normal', 'adaptasi kebiasaan baru',
            'satgas covid', 'gugus tugas', 'kemenkes', 'who', 'unicef'
        ]
        
        # ✅ DAFTAR TOPIK YANG DITOLAK
        self.rejected_topics = [
            'makanan', 'minuman', 'restoran', 'warung', 'kue', 'cheesecake',
            'musik', 'lagu', 'artis', 'band', 'snsd', 'bts', 'blackpink',
            'film', 'drama', 'sinetron', 'netflix', 'youtube',
            'olahraga', 'sepak bola', 'bulutangkis', 'tenis',
            'game', 'mobile legend', 'free fire', 'pubg',
            'politik', 'presiden', 'menteri', 'jokowi', 'prabowo',
            'hiburan', 'wisata', 'travel', 'liburan',
            'universitas', 'kampus', 'sekolah', 'pelajaran'
        ]
        
        # ✅ DAFTAR KATA BERBAHAYA
        self.dangerous_keywords = [
            'bunuh diri', 'melukai', 'bunuh', 'racun', 'bom', 'senjata',
            'kekerasan', 'teror', 'extrem', 'radikal'
        ]

    def validate_input(self, query: str) -> Tuple[bool, str]:
        """Guard rail untuk input query dari user"""
        query_lower = query.lower()
        
        # 1. Cek topik ditolak
        for topic in self.rejected_topics:
            if topic in query_lower:
                return False, f"❌ Maaf, saya hanya dapat menjawab pertanyaan tentang COVID-19 di Indonesia."
        
        # 2. Cek kata berbahaya
        for danger in self.dangerous_keywords:
            if danger in query_lower:
                return False, "❌ Pertanyaan mengandung konten yang tidak aman."
        
        # 3. Cek apakah query tentang COVID
        is_covid_related = any(keyword in query_lower for keyword in self.covid_keywords)
        if not is_covid_related:
            return False, "❌ Maaf, saya hanya dapat menjawab pertanyaan tentang COVID-19 di Indonesia."
        
        return True, "OK"

    def validate_output(self, answer: str, question: str, contexts: List[str]) -> Tuple[bool, str]:
        """Guard rail untuk output dari LLM"""
        answer_lower = answer.lower()
        question_lower = question.lower()
        
        # 1. Cek jika LLM menolak menjawab
        rejection_phrases = [
            'maaf', 'tidak tahu', 'tidak bisa', 'tidak ditemukan',
            'informasi tidak ada', 'diluar pengetahuan', 'sebagai ai',
            'saya tidak', 'belum diprogram', 'tidak tersedia'
        ]
        
        if any(phrase in answer_lower for phrase in rejection_phrases):
            return True, "OK"  # Biarkan rejection messages pass
        
        # 2. Cek topik ditolak dalam jawaban
        for topic in self.rejected_topics:
            if topic in answer_lower:
                return False, "❌ Maaf, informasi tidak ditemukan dalam dokumen sumber COVID-19 Indonesia."
        
        # 3. Cek kata berbahaya dalam jawaban
        for danger in self.dangerous_keywords:
            if danger in answer_lower:
                return False, "❌ Jawaban mengandung konten yang tidak aman."
        
        # 4. Cek konsistensi dengan context
        if not self._check_context_consistency(answer, contexts):
            return False, "❌ Maaf, informasi tidak ditemukan dalam dokumen sumber COVID-19 Indonesia."
        
        # 5. Cek apakah jawaban tentang COVID untuk pertanyaan COVID
        if any(keyword in question_lower for keyword in ['covid', 'corona', 'virus', 'pandemi']):
            has_covid_keywords = any(keyword in answer_lower for keyword in self.covid_keywords[:20])
            if not has_covid_keywords:
                return False, "❌ Maaf, informasi tidak ditemukan dalam dokumen sumber COVID-19 Indonesia."
        
        return True, "OK"

    def _check_context_consistency(self, answer: str, contexts: List[str]) -> bool:
        """Cek apakah jawaban konsisten dengan context - LEBIH TOLERAN"""
        if not contexts:
            return False
            
        # Gabungkan semua context
        all_context = " ".join(contexts).lower()
        answer_lower = answer.lower()
        
        # Cek kata kunci penting dari context ada di jawaban
        context_keywords = set()
        for context in contexts:
            words = context.lower().split()[:15]  # Ambil lebih banyak kata
            context_keywords.update([w for w in words if len(w) > 3])
        
        # Hitung berapa banyak keyword context yang muncul di jawaban
        matching_keywords = sum(1 for keyword in context_keywords if keyword in answer_lower)
        
        # ✅ PERBAIKAN: Lower threshold dari 2 menjadi 1
        return matching_keywords >= 1

    
    def emergency_shutdown(self, answer: str) -> bool:
        """Emergency shutdown untuk jawaban yang sangat berbahaya"""
        emergency_phrases = [
            'bunuh diri', 'bunuh dirimu', 'racun', 'bom', 'senjata api',
            'kekerasan seksual', 'perkosaan', 'aniaya', 'siksa'
        ]
        
        answer_lower = answer.lower()
        return any(phrase in answer_lower for phrase in emergency_phrases)