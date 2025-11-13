from fastapi import FastAPI, HTTPException
import requests

app = FastAPI(
    title="Local Weather Tracker - Milestone 1",
    description="Milestone 1: Call external weather API and return the response.",
    version="1.0.0"
)

# External API URLs from project description
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


@app.get("/health")
def health_check():
    return {"status": "ok", "milestone": 1}


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


@app.post("/ingest")
def ingest(city: str, country: str):
    lat, lon, resolved_city, resolved_country = geocode_city(city, country)
    cw = fetch_weather(lat, lon)

    return {
        "city": resolved_city,
        "country": resolved_country,
        "latitude": lat,
        "longitude": lon,
        "temperature_c": cw["temperature"],
        "windspeed_kmh": cw["windspeed"],
        "observation_time": cw["time"],
        "notes": None
    }
