import boto3
import json
import os
from botocore.exceptions import ClientError, NoCredentialsError

class RagService:
    def __init__(self):
        self.kendra_index_id = os.getenv('KENDRA_INDEX_ID', 'mock-index')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        try:
            self.kendra_client = boto3.client('kendra', region_name=self.region)
            self.use_aws = True
        except NoCredentialsError:
            print("Warning: No AWS Credentials found. Using Mock RAG.")
            self.use_aws = False
        except Exception as e:
            print(f"Warning: Failed to init Kendra client: {e}. Using Mock RAG.")
            self.use_aws = False

        # Enhanced Mock Data for Fallback (Regional & Central Schemes)
        self.mock_data = [
            {
                "text": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi): Provides 6,000 INR per year in three installments to small and marginal farmers.",
                "keywords": ["kisan", "money", "6000", "farmer", "agriculture"],
                "link": "https://pmkisan.gov.in/"
            },
            {
                "text": "Janani Suraksha Yojana (JSY): A safe motherhood intervention providing 1,400 INR for rural and 1,000 INR for urban institutional deliveries.",
                "id": "pm-kisan",
                "text": "PM-KISAN Scheme: Provides ₹6,000 per year income support to small farmers in 3 equal installments.",
                "keywords": ["kisan", "farmer", "money", "fund", "6000", "pm kisan"],
                "link": "https://pmkisan.gov.in",
                "title": "PM-KISAN Samman Nidhi",
                "benefit": "₹6,000/year Income Support",
                "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/9/95/Digital_India_logo.svg/1200px-Digital_India_logo.svg.png" 
            },
            {
                "id": "ayushman",
                "text": "Ayushman Bharat: Provides health insurance coverage of ₹5 Lakh per family per year for secondary and tertiary care hospitalization.",
                "keywords": ["health", "insurance", "medical", "hospital", "ayushman", "treatment"],
                "link": "https://pmjay.gov.in",
                "title": "Ayushman Bharat - PMJAY",
                "benefit": "₹5 Lakh Free Treatment",
                "logo": "https://pmjay.gov.in/sites/default/files/2019-02/pmjay-logo-new.png"
            },
            {
                "id": "enam",
                "text": "e-NAM (National Agriculture Market): An electronic trading portal which networks existing APMC mandis to create a unified national market for agricultural commodities.",
                "keywords": ["mandi", "market", "price", "sell", "enam", "trading"],
                "link": "https://enam.gov.in",
                "title": "e-NAM (National Agriculture Market)",
                "benefit": "Better Prices for Crops",
                "logo": "https://enam.gov.in/web/assets/images/logo.png"
            },
            {
               "id": "fasal-bima",
               "text": "Pradhan Mantri Fasal Bima Yojana (PMFBY): Crop insurance scheme that provides financial support to farmers suffering crop loss/damage arising out of unforeseen events.",
               "keywords": ["crop", "damage", "bima", "insurance", "loss", "cyclone"],
               "link": "https://pmfby.gov.in",
               "title": "PM Fasal Bima Yojana",
               "benefit": "Crop Loss Insurance",
               "logo": "https://pmfby.gov.in/assets/images/logo.png"
            },
             {
               "id": "ujjwala",
               "text": "PM Ujjwala Yojana: Provides clean cooking fuel (LPG connections) to poor households to prevent health hazards associated with cooking based on fossil fuel.",
               "keywords": ["gas", "lpg", "cooking", "cylinder", "ujjwala", "fuel"],
               "link": "https://www.pmuy.gov.in/",
               "title": "PM Ujjwala Yojana",
               "benefit": "Free LPG Connection",
               "logo": "https://www.pmuy.gov.in/images/logo.png"
            }
        ]

    def retrieve(self, query):
        """
        Retrieves relevant documents. 
        Prioritizes Kendra, falls back to Mock Data.
        """
        print(f"Retrieving for: {query}")
        
        # 1. AWS Kendra Search (If configured)
        if self.use_aws and self.kendra_index_id != 'mock-index':
            try:
                response = self.kendra_client.retrieve(
                    IndexId=self.kendra_index_id,
                    QueryText=query,
                    PageSize=3
                )
                results = [item['Content'] for item in response['ResultItems']]
                if results:
                    return results
            except Exception as e:
                print(f"Kendra Error: {e}")

        # 2. Fallback / Mock Logic
        query_lower = query.lower()
        mock_results = []
        for doc in self.mock_data:
            match = False
            for kw in doc['keywords']:
                if kw in query_lower:
                    match = True
                    break
            
            if match:
                # Format as a structured JSON string so the frontend can parse it if needed, 
                # or just plain text for LLM.
                # For the Hybrid UI (LLM + Cards), we return the text for the LLM 
                # AND we can append a special marker or handle the object retrieval separately.
                # Here we simply return the rich text expecting Bedrock to use it,
                # BUT we also tag it so the frontend could potentially extract it if we passed raw objects.
                # For simplicity in this hackathon phase, we will return the text for the LLM.
                
                # However, to enable the "Scheme Card" on frontend, we need the frontend to receive this structured data.
                # The 'retrieve' method is currently only returning strings for the LLM Context.
                # We need to change the API response structure to send these 'sources' back.
                # For now, let's keep this returning Text for Bedrock context.
                # The 'Server.py' /query endpoint calls this. We will modify Server.py to also fetch 'sources'.
                
                entry = f"{doc['text']} [Source: {doc['link']}]"
                mock_results.append(entry)
        
        # Combine results, prioritizing Kendra but adding mock if relevant
        final_results = mock_results # Prioritize our rich mock data for the demo
        
        if not final_results:
            return ["I do not have specific public data on this local query yet. Please check official portals like india.gov.in."]
            
        return final_results[:5] 

    def get_structured_sources(self, query):
        """
        New method explicitly for UI Cards.
        Returns the full dict objects for matching schemes.
        """
        query_lower = query.lower()
        matches = []
        for doc in self.mock_data:
            for kw in doc['keywords']:
                if kw in query_lower:
                    matches.append(doc)
                    break
        return matches[:3]
