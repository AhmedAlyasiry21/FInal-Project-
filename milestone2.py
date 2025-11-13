from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from typing import Optional, List

app = FastAPI(
    title="Local Weather Tracker - Milestone 2",
    description="Milestone 2: In-memory CRUD for weather observations.",
    version="2.0.0"
)



GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"




class ObservationCreate(BaseModel):
    city: str
    country: str


class ObservationUpdate(BaseModel):
    notes: str


class Observation(BaseModel):
    id: int
    city: str
    country: str
    latitude: float
    longitude: float
    temperature_c: float
    windspeed_kmh: float
    observation_time: str
    notes: Optional[str] = None



observations: List[dict] = []
next_id: int = 1




def geocode_city(city: str, country: str):
    params = {"name": city, "country": country, "count": 1}
    response = requests.get(GEOCODE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    if "results" not in data or not data["results"]:
        raise HTTPException(status_code=404, detail="City not found")

    first = data["results"][0]
    return (
        first["latitude"],
        first["longitude"],
        first["name"],
        first["country"]
    )


def fetch_weather(latitude: float, longitude: float):
    params = {"latitude": latitude, "longitude": longitude, "current_weather": True}
    response = requests.get(WEATHER_URL, params=params)
    response.raise_for_status()
    data = response.json()
    current_weather = data.get("current_weather")

    if not current_weather:
        raise HTTPException(status_code=500, detail="No current weather returned")

    return current_weather




@app.get("/health")
def health_check():
    return {"status": "ok", "milestone": 2}




@app.post("/ingest", response_model=Observation)
def ingest(city: str, country: str):
    """
    Fetch live weather, save it to in-memory list, and return the new observation.
    This is like the final project's POST /ingest, but using in-memory storage.
    """
    global next_id

  
    lat, lon, resolved_city, resolved_country = geocode_city(city, country)

  
    cw = fetch_weather(lat, lon)

    
    obs = {
        "id": next_id,
        "city": resolved_city,
        "country": resolved_country,
        "latitude": lat,
        "longitude": lon,
        "temperature_c": cw["temperature"],
        "windspeed_kmh": cw["windspeed"],
        "observation_time": cw["time"],
        "notes": None
    }

    observations.append(obs)
    next_id += 1

    return obs



@app.get("/observations", response_model=List[Observation])
def list_observations():
    """
    Return all stored observations (from in-memory list).
    """
    return observations




@app.get("/observations/{obs_id}", response_model=Observation)
def get_observation(obs_id: int):
    """
    Return a single observation by ID.
    """
    for obs in observations:
        if obs["id"] == obs_id:
            return obs

    raise HTTPException(status_code=404, detail="Observation not found")




@app.put("/observations/{obs_id}", response_model=Observation)
def update_observation(obs_id: int, update: ObservationUpdate):
    """
    Update the 'notes' field of an observation.
    """
    for obs in observations:
        if obs["id"] == obs_id:
            obs["notes"] = update.notes
            return obs

    raise HTTPException(status_code=404, detail="Observation not found")




@app.delete("/observations/{obs_id}")
def delete_observation(obs_id: int):
    """
    Delete an observation by ID.
    """
    for index, obs in enumerate(observations):
        if obs["id"] == obs_id:
            observations.pop(index)
            return {"deleted": obs_id}

    raise HTTPException(status_code=404, detail="Observation not found")
