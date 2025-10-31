import numpy as np
import faiss
import os
import json
from sentence_transformers import SentenceTransformer

class Retriever:
    def __init__(self, index_path=None, texts_path=None):
        from src import config
        
        if index_path is None:
            index_path = config.INDEX_PATH
        if texts_path is None:
            texts_path = config.TEXT_PATH
        
        self.index_path = index_path
        self.texts_path = texts_path
        self.embedder = None
        self.index = None
        self.texts = None
        self.default_top_k = 15
        self.score_threshold = 0.1
        
        print(f"🔍 Retriever path info:")
        print(f"  - Index: {index_path}")
        print(f"  - Texts: {texts_path}")
        print(f"  - Index exists: {os.path.exists(index_path)}")
        print(f"  - Texts exists: {os.path.exists(texts_path)}")
        
        self._load_components()
    
    def _load_components(self):
        """Load model dan index - VERSI SANGAT SEDERHANA"""
        try:
            print("🔄 Loading embedder...")
            self.embedder = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
            
            print("🔄 Loading FAISS index...")
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                print(f"✅ FAISS index loaded: {self.index_path}")
                print(f"📊 Index size: {self.index.ntotal} vectors")
            else:
                raise FileNotFoundError(f"FAISS index not found: {self.index_path}")
            
            print("🔄 Loading texts...")
            if os.path.exists(self.texts_path):
                with open(self.texts_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"📊 Raw data type: {type(data)}")
                
                if isinstance(data, list):
                    self.texts = []
                    for item in data:
                        if isinstance(item, str):
                            self.texts.append(item)
                        elif isinstance(item, dict):
                            if 'text' in item:
                                self.texts.append(str(item['text']))
                            else:
                                self.texts.append(str(item))
                        else:
                            self.texts.append(str(item))
                else:
                    self.texts = [str(data)]
                
                print(f"✅ Loaded {len(self.texts)} text chunks")
                
                if len(self.texts) != self.index.ntotal:
                    print(f"⚠️  WARNING: Texts ({len(self.texts)}) != Index ({self.index.ntotal})")
                    if len(self.texts) > self.index.ntotal:
                        self.texts = self.texts[:self.index.ntotal]
                    else:
                        self.texts.extend([''] * (self.index.ntotal - len(self.texts)))
                    print(f"⚠️  Adjusted texts to: {len(self.texts)}")
                        
            else:
                raise FileNotFoundError(f"Texts file not found: {self.texts_path}")
                
            print("✅ All components loaded successfully!")
                
        except Exception as e:
            print(f"❌ Error loading components: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            raise e

    def search(self, query, top_k=None):
        """Search similar documents"""
        if self.index is None or self.texts is None:
            raise ValueError("Index belum dimuat!")
        
        if top_k is None:
            top_k = self.default_top_k
        
        try:
            query_embedding = self.embedder.encode([query], convert_to_numpy=True).astype("float32")
            
            scores, indices = self.index.search(query_embedding, top_k)
            
            score_threshold = self.score_threshold
            
            covid_keywords = ['covid', 'corona', 'virus', 'pandemi', 'vaksin', 'gejala']
            query_lower = query.lower()
            is_covid_question = any(keyword in query_lower for keyword in covid_keywords)
            
            if not is_covid_question:
                score_threshold = 0.5
            
            results = []
            for i, (idx, score) in enumerate(zip(indices[0], scores[0])):
                if 0 <= idx < len(self.texts) and score > score_threshold:
                    text = self.texts[idx]
                    if not isinstance(text, str):
                        text = str(text)
                    
                    normalized_score = 1.0 / (1.0 + np.exp(-score))
                    
                    results.append({
                        "text": text,
                        "score": float(normalized_score),
                        "original_score": float(score),
                        "rank": i + 1,
                        "doc_id": int(idx)
                    })
            
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results
            
        except Exception as e:
            print(f"❌ Error dalam search: {e}")
            return []

    def smart_search(self, query):
        """Smart search fallback"""
        return self.search(query)