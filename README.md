# Local Weather Tracker API
Ahmed Alyasiry
CSIS-1230 – Fall 2024

This project is a FastAPI-based application that retrieves real-time weather data using the Open-Meteo API, stores results in PostgreSQL, and allows users to manage weather observations through a REST API.

This application was developed as the final project for CSIS-1230.

---

## Features

- Fetch live weather data by city and country  
- Store weather observations in PostgreSQL  
- Retrieve, update, and delete records  
- REST API powered by FastAPI  
- Automatic API documentation via Swagger UI  

---

## Technology Stack

Backend: FastAPI (Python)  
Database: PostgreSQL  
HTTP Client: Requests  
Server: Uvicorn  
Database Driver: Psycopg2  

---

## Project Structure


---

## How to Run the Application

1. Navigate to the project folder and activate the virtual environment:

```bash
cd FinalProject
source venv/bin/activate
uvicorn milestone4:app --reload
Open the following URLs in your browser:

http://127.0.0.1:8000
 — Root endpoint

http://127.0.0.1:8000/docs
 — Interactive Swagger documentation
 CREATE TABLE observations (
    id SERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    temperature_c REAL NOT NULL,
    windspeed_kmh REAL NOT NULL,
    observation_time TEXT NOT NULL,
    notes TEXT
);

