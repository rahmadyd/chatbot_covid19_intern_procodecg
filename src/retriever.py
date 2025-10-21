import os
import faiss
import json
from sentence_transformers import SentenceTransformer
from .config import MODEL_CONFIG, INDEX_PATH, TEXT_PATH


class Retriever:
    def __init__(self):
        print("🔄 Loading Retriever...")

        # Load model embedding
        self.embedding_model = SentenceTransformer(
            MODEL_CONFIG["embedding_model"],
            device=MODEL_CONFIG["device"]
        )

        # Validasi file index dan teks
        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(f"❌ File index tidak ditemukan di: {INDEX_PATH}")
        if not os.path.exists(TEXT_PATH):
            raise FileNotFoundError(f"❌ File teks tidak ditemukan di: {TEXT_PATH}")

        # Load FAISS index
        self.index = faiss.read_index(INDEX_PATH)

        # Load teks dokumen
        with open(TEXT_PATH, "r", encoding="utf-8") as f:
            self.texts = json.load(f)

        self.top_k = MODEL_CONFIG.get("top_k", 3)

        print(f"✅ Retriever ready! Loaded {self.index.ntotal} vectors dari {INDEX_PATH}")

    def search(self, query: str):
        """Cari teks paling relevan untuk query yang diberikan."""
        query_vector = self.embedding_model.encode([query])
        query_vector = query_vector.astype("float32")

        # 👉 gunakan FAISS API yang benar
        distances, indices = self.index.search(query_vector, self.top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if 0 <= idx < len(self.texts):
                results.append({
                    "text": self.texts[idx],
                    "score": float(distances[0][i])
                })

        return results
