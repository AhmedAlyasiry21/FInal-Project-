#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests

def get_city_coordinates(city: str, country: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "country": country}
    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}")

    data = response.json()
    if not data.get("results"):
        raise Exception("No results found for city")

    first = data["results"][0]
    return {
        "city": first.get("name"),
        "country": first.get("country"),
        "latitude": first.get("latitude"),
        "longitude": first.get("longitude")
    }

if __name__ == "__main__":
    try:
        coords = get_city_coordinates("Chicago", "US")
        print("Server Response:")
        print(coords)
    except Exception as e:
        print("Error:", e)

