from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import hashlib

app = FastAPI()

DATA_FILE = "backend/art_pieces.json"


# ------------- Helper Functions -------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_id(combined: str):
    return hashlib.md5(combined.encode()).hexdigest()[:8]


# ------------- Data Models -------------
class ArtPiece(BaseModel):
    author: str
    name: str
    form: str
    created_year: int
    location: str
    description: str = ""


# ------------- API Endpoints -------------
@app.get("/art")
def get_all_art():
    data = load_data()
    return data

@app.get("/art/{art_id}")
def get_single_art(art_id: str):
    data = load_data()
    return data[art_id]

@app.post("/art")
def add_art(item: ArtPiece):
    data = load_data()

    combined = f"{item.author}-{item.name}-{item.form}-{item.created_year}-{item.location}-{item.description[:20]}"
    art_id = generate_id(combined)

    if art_id in data:
        raise HTTPException(status_code=400, detail="Art already exists")

    data[art_id] = item.dict()
    save_data(data)
    return {"id": art_id, "message": "Art added"}

@app.put("/art/{art_id}")
def update_art(art_id: str, item: ArtPiece):
    data = load_data()

    if art_id not in data:
        raise HTTPException(status_code=404, detail="Art not found")

    data[art_id] = item.dict()
    save_data(data)
    return {"message": "Art updated"}

@app.delete("/art/{art_id}")
def delete_art(art_id: str):
    data = load_data()

    if art_id not in data:
        raise HTTPException(status_code=404, detail="Art not found")

    del data[art_id]
    save_data(data)
    return {"message": "Art deleted"}
