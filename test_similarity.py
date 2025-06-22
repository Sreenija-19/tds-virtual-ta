import requests

url = "http://127.0.0.1:8000/similarity"
payload = {
    "docs": [
        "The quick brown fox jumps over the lazy dog.",
        "FastAPI is a modern web framework for building APIs with Python.",
        "OpenAI provides powerful AI models for developers."
    ],
    "query": "What is FastAPI?"
}
response = requests.post(url, json=payload)
print(response.json())