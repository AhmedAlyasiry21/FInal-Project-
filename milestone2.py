#!/usr/bin/env python
# coding: utf-8

# In[12]:


from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


# In[13]:


# simple in-memory "database"
observations = []
next_id = 1

def find_observation(obs_id: int):
    """Return observation dict or None."""
    for obs in observations:
        if obs["id"] == obs_id:
            return obs
    return None


# In[14]:


def fetch_observation_from_api(city: str, country: str):
    """
    Uses the same flow as Milestone 1:
      1) Geocoding: city,country -> latitude, longitude (+ normalized city/country)
      2) Weather: latitude, longitude -> temperature_c, windspeed_kmh, observation_time
    Returns a dict with the exact field names used in Milestone 1.
    """
    # 1) Geocoding
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": city, "country": country, "count": 1}
    geo_resp = requests.get(geo_url, params=geo_params, timeout=10)
    if geo_resp.status_code != 200:
        raise Exception(f"Geocoding failed: {geo_resp.status_code}")
    geo = geo_resp.json()
    if not geo.get("results"):
        raise Exception("No geocoding results for that city/country")

    g0 = geo["results"][0]
    city = g0.get("name", city)
    country = g0.get("country_code") or g0.get("country") or country
    latitude = float(g0["latitude"])
    longitude = float(g0["longitude"])

    # 2) Weather
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {"latitude": latitude, "longitude": longitude, "current_weather": True}
    w_resp = requests.get(weather_url, params=weather_params, timeout=10)
    if w_resp.status_code != 200:
        raise Exception(f"Weather failed: {w_resp.status_code}")
    current = (w_resp.json()).get("current_weather") or {}

    temperature_c = current.get("temperature")
    windspeed_kmh = current.get("windspeed")
    observation_time = current.get("time")
    if temperature_c is None or windspeed_kmh is None or observation_time is None:
        raise Exception("Missing fields in weather response")

    return {
        "city": city,
        "country": str(country),
        "latitude": latitude,
        "longitude": longitude,
        "temperature_c": float(temperature_c),
        "windspeed_kmh": float(windspeed_kmh),
        "observation_time": observation_time,
    }


# In[15]:


# ---- Home (clickable) ----
@app.route("/", methods=["GET"])
def home():
    # simple page with links + a POST form so you can click and see results
    return (
        "<h2>Local Weather Tracker — Milestone 2</h2>"
        "<p>This server is in sync with Milestone 1. Use the links and form below.</p>"
        "<h3>Read</h3>"
        "<ul>"
        "<li><a href='/observations'>GET /observations</a></li>"
        "<li>After creating one: <code>/observations/1</code> etc.</li>"
        "</ul>"
        "<h3>Create (POST /ingest)</h3>"
        "<form method='post' action='/ingest'>"
        "City: <input name='city' value='Chicago'/> "
        "Country: <input name='country' value='US'/> "
        "<button type='submit'>Create</button>"
        "</form>"
        "<p><em>Tip:</em> The form sends POST so you can create by clicking.</p>"
    )

# ---- CREATE (uses Milestone 1 logic) ----
@app.route("/ingest", methods=["POST"])
def create_observation():
    """
    Accepts city/country via either query string or form fields.
    Fills ALL fields using Milestone 1 (Open-Meteo) logic.
    """
    global next_id

    city = (request.args.get("city") or request.form.get("city") or "").strip()
    country = (request.args.get("country") or request.form.get("country") or "").strip()
    if not city or not country:
        return jsonify({"error": "Both 'city' and 'country' are required"}), 400

    try:
        data = fetch_observation_from_api(city, country)
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    obs = {
        "id": next_id,
        "city": data["city"],
        "country": data["country"],
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "temperature_c": data["temperature_c"],
        "windspeed_kmh": data["windspeed_kmh"],
        "observation_time": data["observation_time"],
        "notes": None
    }
    observations.append(obs)
    next_id += 1
    return jsonify(obs), 201

# ---- READ: all ----
@app.route("/observations", methods=["GET"])
def list_observations():
    return jsonify(observations), 200

# ---- READ: one ----
@app.route("/observations/<int:obs_id>", methods=["GET"])
def get_observation(obs_id: int):
    obs = find_observation(obs_id)
    if obs:
        return jsonify(obs), 200
    return jsonify({"error": "Not found"}), 404

# ---- UPDATE: notes only ----
@app.route("/observations/<int:obs_id>", methods=["PUT"])
def update_observation(obs_id: int):
    obs = find_observation(obs_id)
    if not obs:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(silent=True) or {}
    if "notes" not in data:
        return jsonify({"error": "Missing 'notes' in JSON body"}), 400
    obs["notes"] = data["notes"]
    return jsonify({"id": obs_id, "notes": obs["notes"]}), 200

# ---- DELETE ----
@app.route("/observations/<int:obs_id>", methods=["DELETE"])
def delete_observation(obs_id: int):
    global observations
    if not find_observation(obs_id):
        return jsonify({"error": "Not found"}), 404
    observations = [o for o in observations if o["id"] != obs_id]
    return jsonify({"deleted": obs_id}), 200

# (optional) quick reset for testing
@app.route("/_reset", methods=["POST"])
def _reset():
    global observations, next_id
    observations = []
    next_id = 1
    return {"ok": True, "next_id": next_id}


# In[16]:


print("Flask server running on http://127.0.0.1:5000")
app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)


# In[ ]:




