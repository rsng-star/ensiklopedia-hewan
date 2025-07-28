from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path
import json

app = FastAPI()

DATA_FILE = Path("data.json")  # Sesuai struktur foldermu

class Animal(BaseModel):
    id: int
    name: str
    group: str
    description: str
    image_url: str

def load_animals() -> List[Animal]:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return [Animal(**item) for item in json.load(f)]
    return []

def save_animals(data: List[Animal]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([a.dict() for a in data], f, indent=2)

@app.get("/animals", response_model=List[Animal])
def get_animals():
    return load_animals()

@app.post("/animals", response_model=Animal)
def add_animal(animal: Animal):
    animals = load_animals()
    if any(a.id == animal.id for a in animals):
        raise HTTPException(status_code=400, detail="ID sudah dipakai.")
    animals.append(animal)
    save_animals(animals)
    return animal

@app.put("/animals/{animal_id}", response_model=Animal)
def update_animal(animal_id: int, updated: Animal):
    animals = load_animals()
    for idx, a in enumerate(animals):
        if a.id == animal_id:
            animals[idx] = updated
            save_animals(animals)
            return updated
    raise HTTPException(status_code=404, detail="Hewan tidak ditemukan.")

@app.delete("/animals/{animal_id}")
def delete_animal(animal_id: int):
    animals = load_animals()
    for idx, a in enumerate(animals):
        if a.id == animal_id:
            del animals[idx]
            save_animals(animals)
            return {"message": "Hewan berhasil dihapus"}
    raise HTTPException(status_code=404, detail="Hewan tidak ditemukan.")
