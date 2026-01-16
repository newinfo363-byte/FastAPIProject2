from fastapi import FastAPI
from pydantic import BaseModel
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from /static (so API routes aren't shadowed)
app.mount("/static", StaticFiles(directory="."), name="static")

# Serve index.html at root
@app.get("/")
def read_index():
    return FileResponse("index.html")

# Data model
class User(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    blood_pressure: Optional[str] = None
    notes: Optional[str] = None

class SearchQuery(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

DATA_FILE = "data.json"

@app.post("/submit")
def save_data(user: User):
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []

    # use Pydantic v2 model_dump() to serialize the model
    data.append(user.model_dump())

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return {"message": "Data saved successfully 🎉"}

@app.get("/entries")
def get_entries():
    """Return the list of stored entries from data.json (empty list if none)."""
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    return data

@app.post("/search")
def search_entries(query: SearchQuery):
    """Return entries matching optional name (case-insensitive substring) and optional exact age."""
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []

    results: List[dict] = []
    for item in data:
        match = True
        if query.name:
            if 'name' not in item or query.name.lower() not in str(item.get('name', '')).lower():
                match = False
        if query.age is not None:
            # If stored item has age, compare; otherwise treat as non-match
            if 'age' not in item or item.get('age') != query.age:
                match = False
        if match:
            results.append(item)
    return results
