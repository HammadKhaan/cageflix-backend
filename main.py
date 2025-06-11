from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import json
import requests


# Load environment variables
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

# Load movie data once at startup
with open("cageflix_movies.json", "r", encoding="utf-8") as f:
    MOVIES = json.load(f)

app = FastAPI(title="Cageflix API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cage-flix.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory poster cache
poster_cache = {}


@app.get("/movies")
def get_movies(genre: str = Query(None)):
    if genre:
        filtered = [
            movie for movie in MOVIES
            if genre.lower() in [g.lower() for g in movie.get("genres", [])]
        ]
        return filtered
    return MOVIES

@app.get("/movies/{movie_id}")
def get_movie_by_id(movie_id: str):
    movie = next((m for m in MOVIES if m['id'] == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.get("/poster/{imdb_id}")
def get_poster(imdb_id: str):
    if imdb_id in poster_cache:
        return {"poster": poster_cache[imdb_id]}

    url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="OMDb API request failed")

    data = response.json()
    if data.get("Response") == "True" and data.get("Poster") and data["Poster"] != "N/A":
        poster_cache[imdb_id] = data["Poster"]
        return {"poster": data["Poster"]}
    else:
        poster_cache[imdb_id] = None
        return {"poster": None}
