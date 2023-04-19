#main.py
from datetime import datetime
from api_clients import get_openweathermap_data, get_yandex_weather_data, get_coordinates
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from database import create_connection, create_tables
from weather_update import _update_weather_data



app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.state.db = await create_connection()
    await create_tables(app.state.db)

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.db.close()


@app.post("/api/v1/cities/")
async def add_city(city: dict):
    
    # Check if the city is valid
    coordinates = await get_coordinates(city["name"])  
    if coordinates is None:
        raise HTTPException(status_code=400, detail="Invalid city name.")
    
    # Insert the new city into the cities table or do nothing if it already exists
    city_id = await app.state.db.fetchval("INSERT INTO cities (name) VALUES ($1) ON CONFLICT (name) DO NOTHING RETURNING id", city["name"])

    if city_id is not None:
        await fetch_and_store_weather_data(city_id, city["name"])  

    return JSONResponse(content=city, status_code=201)


@app.get("/api/v1/cities/")
async def get_cities():
    # Retrieve a list of all cities from the cities table
    cities = await app.state.db.fetch("SELECT name FROM cities")
    return {"result": [city["name"] for city in cities]}

@app.get("/api/v1/cities/{city_name}/")
async def get_city_weather(city_name: str):
    # Retrieve the latest weather data for the city from the weather_data table
    city = await app.state.db.fetchrow("SELECT * FROM cities WHERE name = $1", city_name)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    weather_data = await app.state.db.fetchrow(
        "SELECT * FROM weather_data WHERE city_id = $1 ORDER BY timestamp DESC",
        city["id"]
    )

    if not weather_data:
        raise HTTPException(status_code=404, detail="Weather data not found")

    return {
        "name": city_name,
        "weather": {
            weather_data["data_source"]: {
                "temperature": weather_data["temperature"],
                "timestamp": weather_data["timestamp"].isoformat(),
            }
        },
    }


@app.get("/api/v1/cities/{city_name}/time/")
async def get_city_weather_with_time(city_name: str, weather_time: str):
    # Convert the weather_time string to a datetime.datetime instance
    weather_time_dt = datetime.fromisoformat(weather_time)

    # Retrieve weather data for the city and timestamp from the weather_data table
    city = await app.state.db.fetchrow("SELECT * FROM cities WHERE name = $1", city_name)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    weather_data = await app.state.db.fetchrow(
        """
        SELECT * FROM weather_data
        WHERE city_id = $1 AND timestamp <= $2
        ORDER BY timestamp DESC
        """,
        city["id"],
        weather_time_dt,
    )

    if not weather_data:
        raise HTTPException(status_code=404, detail="Weather data not found")

    return {
        "name": city_name,
        "weather": {
            weather_data["data_source"]: {
                "temperature": weather_data["temperature"],
                "timestamp": weather_data["timestamp"].isoformat(),
            }
        },
    }


async def fetch_and_store_weather_data(city_id: int, city_name: str):
    lat, lon = await get_coordinates(city_name)

    openweathermap_data = await get_openweathermap_data(lat, lon)
    yandex_weather_data = await get_yandex_weather_data(lat, lon)

    if openweathermap_data and "main" in openweathermap_data:
        temperature = openweathermap_data["main"]["temp"] - 273.15
        timestamp = datetime.now()

        await app.state.db.execute("""
        INSERT INTO weather_data (city_id, data_source, temperature, timestamp)
        VALUES ($1, 'OpenWeatherMap', $2, $3)
        """, city_id, temperature, timestamp)

    if yandex_weather_data and "fact" in yandex_weather_data["forecasts"][0]:
        temperature = yandex_weather_data["forecasts"][0]["fact"]["temp"] - 273.15
        timestamp = datetime.now()

        await app.state.db.execute("""
        INSERT INTO weather_data (city_id, data_source, temperature, timestamp)
        VALUES ($1, 'Yandex', $2, $3)
        """, city_id, temperature, timestamp)

       