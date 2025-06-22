from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import numpy as np
import openai
import csv
import os
import requests
import json

app = FastAPI()

# Enable CORS for all origins (GET only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Path to the uploaded CSV file
CSV_FILE = os.path.join(os.path.dirname(__file__), "q-fastapi.csv")

# Load CSV data on startup
students_data = []

@app.on_event("startup")
def load_students():
    global students_data
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        students_data = [
            {
                "studentId": int(row["studentId"]),
                "class": row["class"]
            }
            for row in reader
        ]

# Main API endpoint
@app.get("/api")
def get_students(class_: Optional[List[str]] = Query(None, alias="class")):
    if class_:
        filtered = [s for s in students_data if s["class"] in class_]
    else:
        filtered = students_data
    return {"students": filtered}

# --- Semantic Similarity Endpoint ---
class SimilarityRequest(BaseModel):
    docs: List[str]
    query: str

class SimilarityResponse(BaseModel):
    matches: List[str]

def get_embedding(text: str) -> List[float]:
    # Replace with your OpenAI API key or use environment variable
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@app.post("/similarity", response_model=SimilarityResponse)
async def similarity_endpoint(payload: SimilarityRequest):
    doc_embeddings = [get_embedding(doc) for doc in payload.docs]
    query_embedding = get_embedding(payload.query)
    doc_embeddings = np.array(doc_embeddings)
    query_embedding = np.array(query_embedding)
    similarities = [cosine_similarity(query_embedding, np.array(doc_emb)) for doc_emb in doc_embeddings]
    # Get indices of top 3 matches
    top_indices = np.argsort(similarities)[::-1][:3]
    matches = [payload.docs[i] for i in top_indices]
    return {"matches": matches}

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
data = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": "Respond in JSON"},
        {"role": "user", "content": "Generate 10 random addresses in the US"}
    ]
}
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    print(json.dumps(result, indent=2))
    with open("openai_response.json", "w") as f:
        json.dump(result, f, indent=2)
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    with open("openai_response.json", "w") as f:
        f.write(f"HTTP error occurred: {http_err}\n{response.text}")
except Exception as err:
    print(f"Other error occurred: {err}")
    with open("openai_response.json", "w") as f:
        f.write(f"Other error occurred: {err}")
