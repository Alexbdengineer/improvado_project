#database.py
import asyncpg
import asyncio
import csv
from config import DATABASE_URL

async def create_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

async def close_connection(conn):
    await conn.close()

async def create_tables(conn):
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS cities (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    );
    """)

    await conn.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        id SERIAL PRIMARY KEY,
        city_id INTEGER REFERENCES cities (id),
        data_source TEXT NOT NULL,
        temperature FLOAT NOT NULL,
        timestamp TIMESTAMP NOT NULL
    );
    """)

async def insert_cities_from_csv(conn, file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        cities_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(cities_reader)  # Skip the header row

        for row in cities_reader:
            city_name = row[0]  # The city name is in the first column
            try:
                await conn.execute("INSERT INTO cities (name) VALUES ($1) ON CONFLICT DO NOTHING", city_name)
                print(f"Inserted {city_name}.")
            except Exception as e:
                print(f"Error inserting {city_name}: {e}")

async def main():
    conn = await create_connection()
    await create_tables(conn)
    await insert_cities_from_csv(conn, "worldcities.csv")
    await close_connection(conn)

if __name__ == "__main__":
    asyncio.run(main())
