"""
RAG Service — Hybrid Knowledge Mesh.
Combines Vector (Semantic), Graph (Relational), and Intent discovery.
"""

import os
import json
import re
from difflib import SequenceMatcher
from botocore.exceptions import ClientError, NoCredentialsError

# Use scikit-learn for professional local RAG
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

class RagService:
    def __init__(self):
        self.kendra_index_id = os.getenv('KENDRA_INDEX_ID', 'mock-index')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.app_context = None # Initialize to avoid lint error
        
        # Initialize AWS Kendra Client
        import boto3
        try:
            self.kendra = boto3.client('kendra', region_name=self.region)
        except Exception:
            self.kendra = None
        
        # Initialize attributes to avoid lint errors
        self.vectorizer = None
        self.vector_matrix = None
        self.corpus = []
        
        # 1. Base Knowledge (Schemes)
        self.schemes = []
        try:
            # Lazy load from DB later to avoid import cycles
            pass
        except Exception as e:
            logger.error(f"DB Scheme Load Error: {e}")

        # 3. Load Uploaded Docs (Local RAG for Citizen Docs)
        self.upload_dir = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
        self._load_uploaded_docs()

        # 4. Initialize Vector Indexing
        if HAS_SKLEARN:
            # Load initial schemes from DB if empty
            if not self.schemes:
                self._load_schemes_from_db()
            self.refresh_vector_index()
    
        # Mocking AWS parts
        self.use_aws = False

    def _load_schemes_from_db(self):
        """Load schemes from SQLite database."""
        try:
            from app.models.models import Scheme
            
            # If app_context is available, use it (for service init)
            if self.app_context:
                with self.app_context:
                    self._query_schemes(Scheme)
            else:
                # If running within a request, db session is already active
                try:
                    self._query_schemes(Scheme)
                except Exception:
                     # Fallback if no context at all
                     pass

        except Exception as e:
            # Silently fail if app context not ready (will retry on first request)
            pass 
            
    def _query_schemes(self, Scheme):
        schemes = Scheme.query.all()
        if schemes:
            self.schemes = [s.to_dict() for s in schemes]
            print(f"Loaded {len(self.schemes)} schemes from DB.")
        else:
            print("No schemes in DB.") 
        
    def set_app_context(self, app_context):
        self.app_context = app_context
        self._load_schemes_from_db()

    def _load_uploaded_docs(self):
        """Read .txt files from uploads/ and add them to the knowledge base."""
        try:
            for filename in os.listdir(self.upload_dir):
                if filename.endswith('.txt'):
                    filepath = os.path.join(self.upload_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                        # Add as a scheme-like object for unified search
                        self.schemes.append({
                            "id": f"upload_{filename}",
                            "title": f"Uploaded Doc: {filename}",
                            "text": text,
                            "keywords": filename.lower().split('.') + ["document", "upload", "my file"],
                            "link": f"/documents/{filename}",
                            "benefit": "Citizen Uploaded Knowledge",
                            "ministry": "User Uploaded",
                            "category": "user_doc",
                            "related": []
                        })
        except Exception as e:
            print(f"Error loading uploaded docs: {e}")

    def refresh_vector_index(self):
        """Update the TF-IDF matrix with current schemes + uploads."""
        if HAS_SKLEARN:
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.corpus = [f"{s['title']} {s['text']} {' '.join(s['keywords'])}" for s in self.schemes]
            self.vector_matrix = self.vectorizer.fit_transform(self.corpus)

    def index_uploaded_document(self, filename, text):
        """Programmatically add a new document to the RAG memory."""
        self.schemes.append({
            "id": f"upload_{filename}",
            "title": f"Document: {filename}",
            "text": text,
            "keywords": filename.lower().split('.') + ["document", "upload"],
            "link": f"/documents/{filename}",
            "benefit": "Citizen Uploaded Knowledge",
            "ministry": "User Uploaded",
            "category": "user_doc",
            "related": []
        })
        self.refresh_vector_index()
        return True

    # ============================================================
    # HYBRID SEARCH (Vector + Graph)
    # ============================================================

    def retrieve(self, query, language='hi', user_profile=None, user_docs=None):
        """Standard retrieval interface — Hybrid: Kendra (Global) + Local (Citizen Docs)."""
        all_matches = []
        
        # Add user documents to temporary search context
        if user_docs:
            for doc in user_docs:
                all_matches.append(f"User Document ({doc['type']}): {doc['filename']} is available.")

        # 1. Kendra Search (Production Global schemes)
        if self.kendra and self.kendra_index_id != 'mock-index':
            kendra_results = self._kendra_search(query)
            all_matches.extend(kendra_results)
            
        # 2. Local Hybrid Search (Mock Schemes + Citizen Uploads)
        # Personalized filtering logic
        scored_docs = self._hybrid_search(query, user_profile=user_profile)
        for doc, _ in scored_docs:
            all_matches.append(f"{doc['text']} [Source: {doc['link']}]")
            
        return all_matches if all_matches else ["I do not have specific public data on this yet. Please visit india.gov.in for official details."]

    def _kendra_search_raw(self, query):
        """Perform real AWS Kendra search and return raw items."""
        if not self.kendra or self.kendra_index_id == 'mock-index':
            return []
        try:
            response = self.kendra.retrieve(
                IndexId=self.kendra_index_id,
                QueryText=query,
                PageSize=3
            )
            return response.get('ResultItems', [])
        except Exception as e:
            print(f"Kendra Error: {e}")
            return []

    def _kendra_search(self, query):
        """Standard Kendra string retrieval."""
        raw_items = self._kendra_search_raw(query)
        results = []
        for item in raw_items:
            text = item.get('Content', '')
            source = item.get('DocumentId', 'Ref')
            results.append(f"{text} [Source: Kendra {source}]")
        return results

    def get_structured_sources(self, query):
        """Detailed data for UI scheme cards — Merges Local + Kendra."""
        final_results = []
        
        # 1. Local Hybrid Search
        local_docs = self._hybrid_search(query)
        for i in range(len(local_docs)):
            if i >= 3: break
            doc, _ = local_docs[i]
            # Create a card from the doc item
            card = {
                "id": str(doc.get('id', '')),
                "title": str(doc.get('title', '')),
                "text": str(doc.get('text', '')),
                "link": str(doc.get('link', '')),
                "benefit": str(doc.get('benefit', '')),
                "logo": str(doc.get('logo', 'https://img.icons8.com/color/96/gov-india.png')),
                "graph_recommendations": []
            }
            related = doc.get('related', [])
            rec_titles = []
            for rid in related:
                scheme = self._get_by_id(rid)
                if scheme:
                    rec_titles.append(str(scheme.get('title', '')))
            card['graph_recommendations'] = rec_titles
            final_results.append(card)

        # 2. Kendra Results (as cards)
        kendra_items = self._kendra_search_raw(query)
        for i in range(len(kendra_items)):
            item = kendra_items[i]
            final_results.append({
                "id": f"kendra-{i}",
                "title": "Official Document (Kendra)",
                "text": str(item.get('Content', ''))[:300] + "...",
                "link": str(item.get('DocumentURI', 'https://india.gov.in')),
                "benefit": "Verified Policy Info",
                "logo": "https://img.icons8.com/color/96/gov-india.png"
            })
            
        return final_results

    def _hybrid_search(self, query, top_k=5, threshold=0.45, user_profile=None):
        """
        Combines TF-IDF Semantic similarity with Keyword overlap.
        Enriched with User Profile boosting for personalization.
        """
        if not query: return []
        
        query_lower = str(query).lower()
        results_map = {} # id -> (doc, score)

        # Profile-based Category Boost
        user_cat = user_profile.get('occupation_category') if user_profile else None
        location = user_profile.get('location') if user_profile else None

        # 1. Vector Search (Semantic)
        if HAS_SKLEARN and self.vectorizer is not None and self.vector_matrix is not None:
            try:
                query_vec = self.vectorizer.transform([query_lower])
                cos_sim = cosine_similarity(query_vec, self.vector_matrix).flatten()
                for idx, score in enumerate(cos_sim):
                    if score > 0.05:
                        did = self.schemes[idx]['id']
                        results_map[did] = (self.schemes[idx], float(score) * 2.0)
            except Exception:
                pass

        # 2. Keyword Overlap (Manual)
        for doc in self.schemes:
            k_score = 0.0
            # Check exact keyword matches
            keywords = doc.get('keywords', [])
            for kw in keywords:
                kw_str = str(kw)
                if f" {kw_str} " in f" {query_lower} ": # Full word match
                    k_score += 0.4
                elif kw_str in query_lower: # Substring match (weaker)
                    k_score += 0.1
            
            # Boost if query contains title
            title = str(doc.get('title', '')).lower()
            if title in query_lower:
                k_score += 0.7

            # PERSONALIZATION BOOST
            if user_cat and doc.get('category') == user_cat:
                k_score += 0.5 # Substantial boost for matching category
            
            if location and location.lower() in str(doc.get('text', '')).lower():
                k_score += 0.3 # Boost for local relevance

            if k_score > 0:
                did = doc['id']
                if did in results_map:
                    results_map[did] = (results_map[did][0], float(results_map[did][1]) + k_score)
                else:
                    results_map[did] = (doc, k_score)

        # Convert map to list and filter by threshold
        final_results = []
        for d, s in results_map.values():
            if float(s) >= threshold:
                final_results.append((d, float(s)))
        
        # Sort and return
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        # Log if we are falling back to search
        if not final_results:
            print(f"DEBUG: [Search] No RAG matches above {threshold}. Falling back to search-based answer.")
            
        # Return slice safely
        limit = min(len(final_results), top_k)
        return final_results[:limit]

    def _get_by_id(self, sid):
        return next((s for s in self.schemes if s['id'] == sid), None)

    # ============================================================
    # INTENT DISCOVERY
    # ============================================================

    def discover_intent(self, query):
        """Classify the user's intent to refine the prompt."""
        q = query.lower()
        if any(w in q for w in ['document', 'certificate', 'patra', 'proof', 'apply']):
            return "DOCUMENTATION_AID"
        if any(w in q for w in ['money', 'cash', 'loan', 'paisa', 'subsidy', 'interest']):
            return "FINANCIAL_SUPPORT"
        if any(w in q for w in ['health', 'hospital', 'medicine', 'ill', 'treatment']):
            return "HEALTHCARE_ACCESS"
        if any(w in q for w in ['job', 'work', 'skill', 'training', 'naukri']):
            return "EMPLOYMENT_LIFELIKE"
        if any(w in q for w in ['mandi', 'price', 'bhaav', 'crop', 'market']):
            return "MARKET_ACCESS"
        return "GENERAL_INQUIRY"

    def get_market_prices(self):
        """Mock Mandi API for Market Access feature."""
        return [
            {"item": "Wheat", "price": "₹2,275", "trend": "up", "demand": "High"},
            {"item": "Mustard", "price": "₹5,400", "trend": "stable", "demand": "Medium"},
            {"item": "Potato", "price": "₹1,200", "trend": "down", "demand": "Low"}
        ]

    def match_livelihood(self, crop_type):
        """
        EXTRAORDINARY FEATURE: Agentic Livelihood matching.
        Matches a farmer's crop to local government buyers or warehouse subsidies.
        """
        matches = {
            "wheat": ["FCI Local Procurement Center", "State Seed Corporation", "PM-Kisan Warehouse Subsidy"],
            "rice": ["State Civil Supplies", "Export Grade A Hub", "Cold Storage Cluster"],
            "mustard": ["Nafed Procurement Point", "Oilseed Cooperative", "Organic Certification Hub"]
        }
        return matches.get(crop_type.lower(), ["Local APMC Mandi", "Cooperative Bank Support"])

    def verify_digital_signature(self, doc_type):
        """Simulates a secure check for 'Zero-Knowledge' digital signatures."""
        return {
            "status": "Verified",
            "provider": "DigiLocker / Bharat-Identity",
            "integrity": "100%",
            "timestamp": "2026-02-14"
        }

    def get_all_schemes(self):
        return self.schemes
