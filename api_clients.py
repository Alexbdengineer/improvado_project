# api_clients.py
import httpx
import config
from typing import Optional, Tuple
from tenacity import retry, wait_exponential
from datetime import datetime

async def get_coordinates(city_name: str) -> Optional[Tuple[float, float]]:
    api_key = config.GOOGLE_MAPS_API_KEY
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={api_key}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

    if data['status'] == 'ZERO_RESULTS':
        return None

    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']
    #print("Obtained coordinates for City:",city_name, "Coords:", lat, lng )

    return lat, lng

# Retry decorator with exponential backoff
@retry(wait=wait_exponential(multiplier=1, min=4, max=30))
async def _get_with_retry(client, url, **kwargs):
    return await client.get(url, **kwargs)


async def get_openweathermap_data(lat: float, lon: float):
    api_key = config.OPENWEATHERMAP_API_KEY
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&lat={lat}&lon={lon}"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await _get_with_retry(client, complete_url)
        return response.json()

async def get_yandex_weather_data(lat: float, lon: float):
    print(f"Getting yandex weather data for coordinates ({lat}, {lon})")
    api_key = config.YANDEX_API_KEY
    base_url = "https://api.weather.yandex.ru/v2/forecast?"
    headers = {"X-Yandex-API-Key": api_key}
    params = {"lat": lat, "lon": lon, "lang": "en_US"}

    try:
        async with httpx.AsyncClient() as client:
            response = await _get_with_retry(client, base_url, headers=headers, params=params)
            print("Got response:", response)
            print("Response status code:", response.status_code)
            return response.json()
    except Exception as e:
        print(f"Error fetching Yandex Weather data: {e}")
        return None



async def fetch_weather_data(city_name):
    lat, lon = await get_coordinates(city_name)

    openweathermap_data = await get_openweathermap_data(lat, lon)
    yandex_weather_data = await get_yandex_weather_data(lat, lon)

    combined_data = {}

    if openweathermap_data is not None and 'main' in openweathermap_data:
        temperature = openweathermap_data['main']['temp'] - 273.15
        timestamp = datetime.now()
        combined_data['openweathermap'] = {
            'temperature': temperature,
            'timestamp': timestamp
        }

    if yandex_weather_data is not None and 'forecasts' in yandex_weather_data and 'fact' in yandex_weather_data['forecasts'][0]:
        temperature = yandex_weather_data['forecasts'][0]['fact']['temp'] - 273.15
        timestamp = datetime.now()
        combined_data['yandex_weather'] = {
            'temperature': temperature,
            'timestamp': timestamp
        }

    return combined_data
