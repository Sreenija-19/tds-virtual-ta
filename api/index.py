from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get_marks(request: Request):
    names = request.query_params.getlist("name")
    # Adjust file path to look for q-vercel-python.json in the parent directory
    file_path = os.path.join(os.path.dirname(__file__), "..", "q-vercel-python.json")
    with open(file_path, "r") as f:
        marks_data = json.load(f)
    name_to_marks = {entry["name"]: entry["marks"] for entry in marks_data}
    marks = [name_to_marks.get(name, None) for name in names]
    return JSONResponse({"marks": marks})
