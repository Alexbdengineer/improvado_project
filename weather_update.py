#weather_update.py
from api_clients import fetch_weather_data
from database import create_connection, close_connection
import asyncio

def _update_weather_data():  
    print("Starting _update_weather_data")  
    asyncio.run(update_weather_data_async())  
    print("Finished _update_weather_data")  


async def update_weather_data_async():  
    conn = await create_connection()
    print('connection to database successful')
    # Retrieve the list of cities from the cities table
    cities = await conn.fetch("SELECT * FROM cities")
    print(f"Found {len(cities)} cities.")  

    async def update_city(city):
        city_name = city["name"]
        print("Processing", city_name)
        city_id = city["id"]
        print("With city ID of", city_id)

        # Fetch the latest weather data from the data sources
        weather_data = await fetch_weather_data(city_name)  
        print("Weather data:", weather_data) # This is as far as the output shows ===CODE PRINTS UP TO THIS POINT
        print(f"Fetching weather data for {city_name}.")  

        for source, data in weather_data.items():
            # Store the updated weather data in the weather_data table
            await conn.execute(
                """
                INSERT INTO weather_data (city_id, data_source, temperature, timestamp)
                VALUES ($1, $2, $3, $4)
                """,
                city_id,
                source,
                data["temperature"],
                data["timestamp"],
            )
            print(f"Inserted data for {city_name} from {source}.")  

    # Update weather data for all cities one by one
    for city in cities:
        await update_city(city)

    await close_connection(conn)
