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

        # Mock Data for Fallback
        self.mock_data = [
            {"text": "PM-KISAN: 6000 INR per year for farmers.", "keywords": ["kisan", "money", "6000"]},
            {"text": "Mandi Prices: Wheat is 2200/quintal in Bhopal.", "keywords": ["mandi", "price", "wheat"]},
            {"text": "Janani Suraksha Yojana: 1400 INR for rural delivery.", "keywords": ["janani", "pregnant", "delivery"]}
        ]

    def retrieve(self, query):
        """
        Retrieves documents from Amazon Kendra. Falls back to keyword search if fails.
        """
        print(f"Retrieving context for: {query} (Mode: {'Kendra' if self.use_aws else 'Mock'})")
        
        if self.use_aws and self.kendra_index_id != 'mock-index':
            try:
                response = self.kendra_client.retrieve(
                    IndexId=self.kendra_index_id,
                    QueryText=query,
                    PageSize=3
                )
                
                results = []
                for item in response.get('ResultItems', []):
                    content = item.get('Content', '')
                    if content:
                        results.append(content)
                
                if results:
                    return results
                else:
                    return ["No relevant documents found in Kendra."]
            
            except Exception as e:
                print(f"Kendra Error: {e}. Falling back to Mock.")
                # Fallthrough to mock
        
        # --- Fallback / Mock Logic ---
        query_lower = query.lower()
        results = []
        for doc in self.mock_data:
            for kw in doc['keywords']:
                if kw in query_lower:
                    results.append(doc['text'])
                    break # Avoid duplicate adds
        
        if not results:
            return ["No specific public data found locally."]
        return results
