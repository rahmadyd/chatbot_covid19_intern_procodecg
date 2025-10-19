 # Script retrieval dari vector DB
 
import faiss
import json
import sentence_transformers
import transformer
import torch
import config
from config import MODEL_CONFIG, INDEX_PATH, TEXT_PATH

index = faiss.read_index(INDEX_PATH)


