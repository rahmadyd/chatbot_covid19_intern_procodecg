import faiss
import os
from src import config

index_path = config.INDEX_PATH
if os.path.exists(index_path):
    index = faiss.read_index(index_path)
    print(f"Index Dimension: {index.d}")
    print(f"Total Vectors: {index.ntotal}")
else:
    print("Index not found")
