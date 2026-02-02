import random

def normalize_intent(query, language):
    """
    Mock function to detect intent. 
    Real implementation would use Amazon Lex or a small LLM classifier.
    """
    # Simple keyword matching for demo
    if 'price' in query.lower() or 'bhav' in query.lower() or 'भाव' in query:
        return {
            'type': 'MARKET_PRICE',
            'entities': {
                'crop': 'Wheat' if 'wheat' in query.lower() or 'गेहूँ' in query else 'Unknown',
                'location': 'UserDistrict' 
            }
        }
    return {'type': 'GENERAL_QUERY'}

def retrieve_context(intent_data):
    """
    Mock RAG Retriever.
    Real implementation queries Amazon Kendra.
    """
    if intent_data.get('type') == 'MARKET_PRICE':
        return [
            {
                'text': 'Mandi Price for Wheat in District X is 2150 INR/Quintal.',
                'source': 'Govt Mandi API - 2023-10-27'
            }
        ]
    return []

def generate_answer(query, context, language):
    """
    Mock LLM Generation.
    Real implementation uses Bedrock (Claude/Titan).
    """
    if not context:
        return "Sorry, I could not find information on that."
    
    # Simple template response based on "retrieved" data
    fact = context[0]['text']
    
    if language == 'hi':
        return f"आपके सवाल का जवाब: {fact} (स्रोत: मंडी एपीआई)"
    else:
        return f"Answer based on records: {fact}"
