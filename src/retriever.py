import numpy as np
import faiss
import os
import json
from sentence_transformers import SentenceTransformer


os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

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
        
        print(f"🔍 Retriever - CONSISTENT MODE")
        self._load_components()
    
    def _load_components(self):
        """Load model dan index"""
        try:
            print("🔄 Loading embedder...")
            self.embedder = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
            
            print("🔄 Loading FAISS index...")
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                print(f"✅ FAISS index loaded: {self.index.ntotal} vectors")
            else:
                raise FileNotFoundError(f"FAISS index not found: {self.index_path}")
            
            print("🔄 Loading texts...")
            if os.path.exists(self.texts_path):
                with open(self.texts_path, 'r', encoding='utf-8') as f:
                    self.texts = json.load(f)
                print(f"✅ Loaded {len(self.texts)} text chunks")
            else:
                raise FileNotFoundError(f"Texts file not found: {self.texts_path}")
                
            print("✅ All components loaded!")
                
        except Exception as e:
            print(f"❌ Error loading components: {e}")
            raise e

    def search(self, query, top_k=None):
        """Search dengan konsistensi lebih baik"""
        if self.index is None or self.texts is None:
            raise ValueError("Index belum dimuat!")
        
        if top_k is None:
            top_k = self.default_top_k
        
        try:
            print(f"🔍 SEARCH: '{query}'")
            
            query_embedding = self.embedder.encode([query], convert_to_numpy=True).astype("float32")
            scores, indices = self.index.search(query_embedding, top_k)
            
            print(f"📊 Raw scores: {scores[0][:5]}")
            
            results = []
            for i, (idx, score) in enumerate(zip(indices[0], scores[0])):
                if 0 <= idx < len(self.texts):
                    text = self.texts[idx]
                    if not isinstance(text, str):
                        text = str(text)
                    
                    if score > self.score_threshold:
                        query_words = set(query.lower().split())
                        text_words = set(text.lower().split())
                        word_overlap = len(query_words.intersection(text_words))
                        
                        if word_overlap >= 1:  
                            results.append({
                                "text": text,
                                "score": float(score),
                                "original_score": float(score),
                                "rank": i + 1,
                                "doc_id": int(idx)
                            })
                            print(f"   ✅ Accepted: score={score:.3f}, overlap={word_overlap}")
            
            print(f"🎯 Final results: {len(results)} documents")
            
            if not results and len(indices[0]) > 0:
                idx = indices[0][0]
                if 0 <= idx < len(self.texts):
                    text = self.texts[idx]
                    results.append({
                        "text": text,
                        "score": 0.5,  # Default score
                        "original_score": float(scores[0][0]),
                        "rank": 1,
                        "doc_id": int(idx)
                    })
                    print(f"🔧 Fallback to top result")
            
            return results[:5]
            
        except Exception as e:
            print(f"❌ Error dalam search: {e}")
            return []

    def search_with_debug(self, query, top_k=None):
        """Search dengan debug info"""
        if self.index is None or self.texts is None:
            return [], {'error': 'Index not loaded'}
        
        if top_k is None:
            top_k = self.default_top_k
        
        try:
            # Encode query
            query_embedding = self.embedder.encode([query], convert_to_numpy=True).astype("float32")
            
            # Search
            scores, indices = self.index.search(query_embedding, top_k)
            
            results = []
            debug_info = {
                'query': query,
                'total_docs_searched': top_k,
                'raw_scores': scores[0][:5].tolist(),
                'found_documents': 0
            }
            
            for i, (idx, score) in enumerate(zip(indices[0], scores[0])):
                if 0 <= idx < len(self.texts):
                    text = self.texts[idx]
                    if not isinstance(text, str):
                        text = str(text)
                    
                    if score > self.score_threshold:
                        query_words = set(query.lower().split())
                        text_words = set(text.lower().split())
                        word_overlap = len(query_words.intersection(text_words))
                        
                        if word_overlap >= 1:
                            results.append({
                                "text": text,
                                "score": float(score),
                                "original_score": float(score),
                                "rank": i + 1,
                                "doc_id": int(idx)
                            })
                            debug_info['found_documents'] += 1
            
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results, debug_info
            
        except Exception as e:
            print(f"❌ Error dalam search: {e}")
            return [], {'error': str(e)}

    def smart_search(self, query):
        return self.search(query)

    def get_index_stats(self):
        """Dapatkan statistik index"""
        if self.index is None:
            return "Index not loaded"
        
        return {
            "total_vectors": self.index.ntotal,
            "total_texts": len(self.texts),
            "embedding_dim": self.index.d,
            "score_threshold": self.score_threshold,
            "default_top_k": self.default_top_k
        }