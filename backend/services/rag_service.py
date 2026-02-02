import json
import os
import numpy as np
# from sentence_transformers import SentenceTransformer
# import faiss

class RagService:
    def __init__(self):
        # We will use valid mock data for the "Working" demo if FAISS is not installed.
        # Installing torch/transformers can be huge (GBs). 
        # To make this "instantly working", we will use a simple Keyword-Match retrieval first.
        # If you want real embeddings, uncomment the imports.
        
        self.data_path = "data/mandi_prices.json"
        
        # Seed some data
        if not os.path.exists("data"):
            os.makedirs("data")
            
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump([
                {"text": "Wheat price in Vidisha is 2150 INR per quintal.", "keywords": ["wheat", "gehu", "vidisha"]},
                {"text": "Rice price in Bhopal is 3200 INR per quintal.", "keywords": ["rice", "chawal", "bhopal"]},
                {"text": "Soybean price in Indore is 4500 INR per quintal.", "keywords": ["soybean", "indore"]},
                {"text": "Govindpura Mandi is closed on Sundays.", "keywords": ["closed", "holiday", "govindpura"]},
            ], f)
            
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)

    def retrieve(self, query):
        """
        Simple keyword based retrieval for speed/robustness in demo.
        """
        query_lower = query.lower()
        results = []
        for doc in self.documents:
            # Check if any keyword matches
            score = 0
            for kw in doc['keywords']:
                if kw in query_lower:
                    score += 1
            
            if score > 0:
                results.append(doc['text'])
        
        if not results:
            return ["No specific data found for this query in the local database."]
        
        return results

    # def retrieve_semantic(self, query):
    #     """
    #     Real FAISS implementation (Uncomment if dependencies installed)
    #     """
    #     model = SentenceTransformer('all-MiniLM-L6-v2')
    #     # ... indexing logic ...
    #     pass
