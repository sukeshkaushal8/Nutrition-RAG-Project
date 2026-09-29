import requests

url = "http://localhost:8000/api/v1/chat"
payload = {"query": "What does WHO recommend for daily salt intake?", "filter_document": None}
try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
