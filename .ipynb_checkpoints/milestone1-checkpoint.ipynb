{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "dcfd3953-5a6b-4d84-9985-209d85c04396",
   "metadata": {},
   "outputs": [],
   "source": [
    "import requests\n",
    "\n",
    "def get_city_coordinates(city: str, country: str):\n",
    "    url = \"https://geocoding-api.open-meteo.com/v1/search\"\n",
    "    params = {\"name\": city, \"country\": country}\n",
    "    response = requests.get(url, params=params, timeout=10)\n",
    "\n",
    "    if response.status_code != 200:\n",
    "        raise Exception(f\"API request failed with status {response.status_code}\")\n",
    "\n",
    "    data = response.json()\n",
    "    if not data.get(\"results\"):\n",
    "        raise Exception(\"No results found for city\")\n",
    "\n",
    "    first = data[\"results\"][0]\n",
    "    return {\n",
    "        \"city\": first.get(\"name\"),\n",
    "        \"country\": first.get(\"country\"),\n",
    "        \"latitude\": first.get(\"latitude\"),\n",
    "        \"longitude\": first.get(\"longitude\")\n",
    "    }\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    try:\n",
    "        coords = get_city_coordinates(\"Chicago\", \"US\")\n",
    "        print(\"Server Response:\")\n",
    "        print(coords)\n",
    "    except Exception as e:\n",
    "        print(\"Error:\", e)\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python [conda env:base] *",
   "language": "python",
   "name": "conda-base-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
