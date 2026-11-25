import requests
from config.settings import OPEN_METEO_TIMEOUT
from core.environment import WeatherData

API_URL = "https://api.open-meteo.com/v1/forecast"


def get_current_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,precipitation,wind_speed_10m",
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }
    response = requests.get(API_URL, params=params, timeout=OPEN_METEO_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    current = payload.get("current")
    if not current:
        raise ValueError("Open-Meteo не повернув блок current")
    return WeatherData(
        temperature_c=float(current["temperature_2m"]),
        precipitation_mm=float(current["precipitation"]),
        wind_kmh=float(current["wind_speed_10m"]),
        source="Open-Meteo API",
        observed_at=str(current.get("time", "not specified")),
    )
