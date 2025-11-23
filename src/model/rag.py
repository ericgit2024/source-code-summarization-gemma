import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os

class RAGEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2', index_path='code_index.faiss', db_path='code_db.pkl'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.code_db = [] # List of dicts: {'code': ..., 'summary': ..., 'metadata': ...}
        self.index_path = index_path
        self.db_path = db_path
        
    def index_codebase(self, data_items):
        """
        data_items: list of dicts with 'code' and 'summary'
        """
        print("Encoding codebase...")
        self.code_db = data_items
        
        codes = [item['code'] for item in data_items]
        embeddings = self.model.encode(codes)
        
        # Initialize FAISS
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        
        print(f"Indexed {len(data_items)} items.")
        self.save_index()
        
    def retrieve(self, query_code, k=3):
        """
        Retrieve top-k similar code snippets
        """
        if not self.index:
            self.load_index()
            if not self.index:
                return []
                
        query_embedding = self.model.encode([query_code])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        
        results = []
        for idx in indices[0]:
            if idx < len(self.code_db):
                results.append(self.code_db[idx])
                
        return results
        
    def save_index(self):
        if self.index:
            faiss.write_index(self.index, self.index_path)
        with open(self.db_path, 'wb') as f:
            pickle.dump(self.code_db, f)
            
    def load_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.db_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.db_path, 'rb') as f:
                self.code_db = pickle.load(f)
            return True
        return False
