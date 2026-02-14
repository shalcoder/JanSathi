import requests
import json

def test_query(query):
    url = "http://localhost:5000/query"
    payload = {"text_query": query, "language": "en"}
    response = requests.post(url, json=payload)
    data = response.json()
    print(f"Query: {query}")
    print(f"Answer Preview: {data['answer']['text'][:150]}...")
    print(f"Context Count: {len(data['context'])}")
    if len(data['context']) > 0:
        print(f"Top Context: {data['context'][0][:100]}...")
    print("-" * 50)

if __name__ == "__main__":
    queries = [
        "Who is Prime Minister?",
        "What is 2 plus 2?",
        "How to cook rice?",
        "PM Kisan scheme benefits"
    ]
    for q in queries:
        test_query(q)
