from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(
    title="Local Weather Tracker - Milestone 4",
    description="Milestone 4: Fully integrated project with PostgreSQL and external API.",
    version="4.0.0"
)

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


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


class ObservationUpdate(BaseModel):
    notes: str


def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password="Eagle2500",
        cursor_factory=RealDictCursor
    )
    return conn


def geocode_city(city: str, country: str):
    params = {"name": city, "country": country, "count": 1}
    response = requests.get(GEOCODE_URL, params=params)
    data = response.json()
    if "results" not in data or not data["results"]:
        raise HTTPException(status_code=404, detail="City not found")
    first = data["results"][0]
    return first["latitude"], first["longitude"], first["name"], first["country"]


def fetch_weather(latitude: float, longitude: float):
    params = {"latitude": latitude, "longitude": longitude, "current_weather": True}
    response = requests.get(WEATHER_URL, params=params)
    data = response.json()
    if "current_weather" not in data:
        raise HTTPException(status_code=500, detail="No current weather returned")
    return data["current_weather"]


@app.get("/health")
def health_check():
    return {"status": "ok", "milestone": 4}


@app.post("/ingest", response_model=Observation)
def ingest(city: str, country: str):
    lat, lon, resolved_city, resolved_country = geocode_city(city, country)
    cw = fetch_weather(lat, lon)
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO observations
                        (city, country, latitude, longitude,
                         temperature_c, windspeed_kmh, observation_time, notes)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, NULL)
                    RETURNING id, city, country, latitude, longitude,
                              temperature_c, windspeed_kmh, observation_time, notes;
                    """,
                    (
                        resolved_city,
                        resolved_country,
                        lat,
                        lon,
                        cw["temperature"],
                        cw["windspeed"],
                        cw["time"]
                    )
                )
                return cur.fetchone()
    finally:
        conn.close()


@app.get("/observations", response_model=List[Observation])
def list_observations():
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, city, country, latitude, longitude,
                           temperature_c, windspeed_kmh, observation_time, notes
                    FROM observations
                    ORDER BY id;
                    """
                )
                return cur.fetchall()
    finally:
        conn.close()


@app.get("/observations/{obs_id}", response_model=Observation)
def get_observation(obs_id: int):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, city, country, latitude, longitude,
                           temperature_c, windspeed_kmh, observation_time, notes
                    FROM observations
                    WHERE id = %s;
                    """,
                    (obs_id,)
                )
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail="Observation not found")
                return row
    finally:
        conn.close()


@app.put("/observations/{obs_id}", response_model=Observation)
def update_observation(obs_id: int, update: ObservationUpdate):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE observations
                    SET notes = %s
                    WHERE id = %s
                    RETURNING id, city, country, latitude, longitude,
                              temperature_c, windspeed_kmh, observation_time, notes;
                    """,
                    (update.notes, obs_id)
                )
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail="Observation not found")
                return row
    finally:
        conn.close()


@app.delete("/observations/{obs_id}")
def delete_observation(obs_id: int):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM observations WHERE id = %s RETURNING id;",
                    (obs_id,)
                )
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail="Observation not found")
                return {"deleted": row["id"]}
    finally:
        conn.close()

@app.get("/")
def root():
    return {"message": "Local Weather Tracker API. Open /docs for the full interface."}
