import json
import boto3
import os
from utils import normalize_intent, retrieve_context, generate_answer

def lambda_handler(event, context):
    """
    Main Orchestrator Lambda.
    1. Receives Input (Text/Audio metadata)
    2. Normalizes Intent
    3. Retrieves Context (RAG)
    4. Generates Answer (LLM)
    5. Returns Response
    """
    print("Received event: " + json.dumps(event, indent=2))
    
    # 1. Parse Input
    try:
        body = json.loads(event.get('body', '{}'))
        user_query = body.get('query')
        user_id = body.get('user_id', 'anonymous')
        language = body.get('language', 'hi') # Default to Hindi
        
        if not user_query:
             return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No query provided'})
            }

        # 2. Intent Normalization
        intent_data = normalize_intent(user_query, language)
        print(f"Normalized Intent: {intent_data}")

        # 3. Retrieval (RAG)
        context_docs = retrieve_context(intent_data)
        print(f"Retrieved Context: {len(context_docs)} documents")

        # 4. Generate Answer
        answer_text = generate_answer(user_query, context_docs, language)
        
        # 5. Delivery (Construct Response)
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'user_id': user_id,
                'query_received': user_query,
                'intent': intent_data,
                'answer': answer_text,
                'sources': [doc['source'] for doc in context_docs]
            })
        }
        
        return response

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
