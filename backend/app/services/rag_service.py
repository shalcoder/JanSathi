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
        self.schemes = [
            {
                "id": "pm-kisan",
                "title": "PM-KISAN Samman Nidhi",
                "text": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi): Provides ₹6,000 per year income support to all landholding farmer families in three equal installments of ₹2,000 each. Launched on 1st December 2018. Eligibility: All landholding farmers. Documents: Aadhaar, bank account, land records. Apply at pmkisan.gov.in or nearest CSC. Helpline: 155261.",
                "keywords": ["kisan", "farmer", "money", "6000", "pm kisan", "agriculture", "farming", "crop", "land", "kisaan"],
                "link": "https://pmkisan.gov.in",
                "benefit": "₹6,000/year Income Support",
                "ministry": "Ministry of Agriculture",
                "category": "agriculture",
                "related": ["fasal-bima", "kisan-credit", "soil-health"]
            },
            {
                "id": "ayushman",
                "title": "Ayushman Bharat - PMJAY",
                "text": "Ayushman Bharat (PM Jan Arogya Yojana): Provides health insurance coverage of ₹5 Lakh per family per year for secondary and tertiary care hospitalization. Covers 1,393 procedures including surgery, medical care, and diagnostics. Eligibility: Based on SECC 2011 deprivation criteria. No premium required. Apply via pmjay.gov.in or Ayushman Mitra at empanelled hospitals.",
                "keywords": ["health", "insurance", "medical", "hospital", "ayushman", "treatment", "disease", "doctor", "medicine", "surgery", "bimari"],
                "link": "https://pmjay.gov.in",
                "benefit": "₹5 Lakh Free Health Cover",
                "ministry": "Ministry of Health",
                "category": "health",
                "related": ["matru-vandana", "jan-aushadhi"]
            },
            {
                "id": "fasal-bima",
                "title": "PM Fasal Bima Yojana (PMFBY)",
                "text": "Pradhan Mantri Fasal Bima Yojana (PMFBY): Crop insurance scheme providing financial support to farmers suffering crop loss from unforeseen events like drought, flood, hailstorm, cyclone, pest attack. Premium: 2% for Kharif, 1.5% for Rabi, 5% for commercial/horticultural crops. Claim within 72 hours of crop damage. Apply via bank, CSC, or pmfby.gov.in.",
                "keywords": ["crop", "damage", "bima", "insurance", "loss", "cyclone", "flood", "drought", "fasal", "weather"],
                "link": "https://pmfby.gov.in",
                "benefit": "Crop Loss Insurance",
                "ministry": "Ministry of Agriculture",
                "category": "agriculture",
                "related": ["pm-kisan", "kisan-credit"]
            },
            {
                "id": "awas",
                "title": "PM Awas Yojana (PMAY)",
                "text": "Pradhan Mantri Awas Yojana: Housing for All by providing affordable housing. Gramin (Rural): Up to ₹1.30 lakh in plains, ₹1.50 lakh in hilly areas for construction of pucca house. Urban: Interest subsidy of 6.5% on home loans for EWS/LIG. Eligibility: No pucca house anywhere in India. Apply via gram panchayat (rural) or ULB (urban).",
                "keywords": ["house", "awas", "ghar", "home", "housing", "construction", "build", "rent", "shelter", "makan"],
                "link": "https://pmaymis.gov.in/",
                "benefit": "₹1.30-2.67 Lakh Housing Aid",
                "ministry": "Ministry of Housing",
                "category": "housing",
                "related": ["jandhan", "saubhagya-bijli"]
            },
            {
                "id": "mudra",
                "title": "PM MUDRA Yojana",
                "text": "Pradhan Mantri MUDRA Yojana: Provides loans up to ₹10 lakh for non-corporate, non-farm small/micro enterprises. Three categories: Shishu (up to ₹50,000), Kishore (₹50,000 to ₹5 lakh), Tarun (₹5 lakh to ₹10 lakh). No collateral required. Apply at any bank, NBFC, or MFI. No processing fee for Shishu loans.",
                "keywords": ["loan", "mudra", "business", "money", "enterprise", "shop", "startup", "self-employed", "vyapaar", "dukaan"],
                "link": "https://www.mudra.org.in/",
                "benefit": "Loans up to ₹10 Lakh",
                "ministry": "Ministry of Finance",
                "category": "financial",
                "related": ["svanidhi", "skill-india"]
            },
            {
                "id": "sukanya",
                "title": "Sukanya Samriddhi Yojana",
                "text": "Sukanya Samriddhi Yojana: Savings scheme for girl child. Interest rate 8.2% p.a. (highest among small savings). Minimum deposit ₹250/year, maximum ₹1.5 lakh/year. Account opens from birth to age 10. Matures at 21 years. 50% withdrawal allowed at age 18 for education. Tax-free under Section 80C.",
                "keywords": ["girl", "daughter", "beti", "education", "savings", "sukanya", "ladki", "bachchi", "school", "college"],
                "link": "https://www.nsiindia.gov.in/",
                "benefit": "8.2% Interest Girl Child Savings",
                "ministry": "Ministry of Finance",
                "category": "education",
                "related": ["matru-vandana", "jandhan"]
            },
            {
                "id": "pm-vishwakarma",
                "title": "PM Vishwakarma Yojana",
                "text": "PM Vishwakarma: Support scheme for traditional artisans and craftspeople working with hands and tools. Covers 18 trades including carpenter, blacksmith, goldsmith, potter, tailor, washerman. Benefits: Recognition (PM Vishwakarma certificate), skill upgradation, toolkit incentive of ₹15,000, collateral-free credit up to ₹3 lakh at 5% interest.",
                "keywords": ["artisan", "craft", "carpenter", "blacksmith", "tailor", "potter", "vishwakarma", "karigar", "mistri", "darzi", "lohar"],
                "link": "https://pmvishwakarma.gov.in/",
                "benefit": "₹15K Toolkit + ₹3 Lakh Loan",
                "ministry": "Ministry of MSME",
                "category": "employment",
                "related": ["mudra", "skill-india"]
            },
            {
                "id": "matru-vandana",
                "title": "PM Matru Vandana Yojana",
                "text": "Pradhan Mantri Matru Vandana Yojana (PMMVY): Cash incentive of ₹11,000 for first child and ₹6,000 for second child (girl only) for pregnant women and lactating mothers. Compensation for wage loss during pregnancy. Eligibility: All pregnant women for first living child. Apply at nearest Anganwadi Centre or health facility.",
                "keywords": ["pregnant", "mother", "baby", "child", "maternity", "birth", "delivery", "garbhwati", "maa", "bachcha"],
                "link": "https://wcd.nic.in/",
                "benefit": "₹6,000-11,000 Maternity Benefit",
                "ministry": "Ministry of Women & Child",
                "category": "health",
                "related": ["ayushman", "jandhan"]
            },
            {
                "id": "jandhan",
                "title": "PM Jan Dhan Yojana",
                "text": "Pradhan Mantri Jan Dhan Yojana: Financial inclusion scheme providing zero-balance bank accounts with RuPay debit card and ₹2 lakh accident insurance. Overdraft facility of ₹10,000 for eligible accounts. Life cover of ₹30,000 for accounts opened before Jan 2015. Apply at any bank branch with Aadhaar/voter ID.",
                "keywords": ["bank", "account", "jan dhan", "debit card", "insurance", "zero balance", "khata", "paisa"],
                "link": "https://pmjdy.gov.in/",
                "benefit": "Zero Balance Bank Account + Insurance",
                "ministry": "Ministry of Finance",
                "category": "financial",
                "related": ["mudra", "awas"]
            },
            {
                "id": "skill-india",
                "title": "Skill India Mission",
                "text": "Skill India Mission: Provides free skill training in 40+ sectors to Indian youth. Includes PMKVY, NAPS, and Jan Shikshan Sansthan. Linkage to employment and entrepreneurship.",
                "keywords": ["training", "skill", "job", "career", "employment", "learning"],
                "link": "https://skillindia.gov.in",
                "benefit": "Certified Skill Training",
                "ministry": "Ministry of Skill Development",
                "category": "employment",
                "related": ["mudra", "pm-vishwakarma"]
            },
            {
                "id": "svanidhi",
                "title": "PM SVANidhi",
                "text": "Micro-credit facility for street vendors to restart their livelihoods. Loans up to ₹50,000 with interest subsidy and digital repayment incentives.",
                "keywords": ["vendor", "street", "loan", "thela", "hawker"],
                "link": "https://pmsvanidhi.mohua.gov.in",
                "benefit": "₹10,000-50,000 Working Capital Loan",
                "ministry": "Ministry of Housing",
                "category": "financial",
                "related": ["mudra", "jandhan"]
            }
        ]

        # 3. Load Uploaded Docs (Local RAG for Citizen Docs)
        self.upload_dir = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
        self._load_uploaded_docs()

        # 4. Initialize Vector Indexing
        if HAS_SKLEARN:
            self.refresh_vector_index()
    
        # Mocking AWS parts
        self.use_aws = False

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

    def retrieve(self, query):
        """Standard retrieval interface — Hybrid: Kendra (Global) + Local (Citizen Docs)."""
        all_matches = []
        
        # 1. Kendra Search (Production Global schemes)
        if self.kendra and self.kendra_index_id != 'mock-index':
            kendra_results = self._kendra_search(query)
            all_matches.extend(kendra_results)
            
        # 2. Local Hybrid Search (Mock Schemes + Citizen Uploads)
        scored_docs = self._hybrid_search(query)
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

    def _hybrid_search(self, query, top_k=5, threshold=0.45):
        """
        Combines TF-IDF Semantic similarity with Keyword overlap.
        Uses a threshold to filter out weak matches (false positives).
        """
        if not query: return []
        
        query_lower = str(query).lower()
        results_map = {} # id -> (doc, score)

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
