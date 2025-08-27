import logging
import requests

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for fetching current weather information."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        logger.info("🌤 Weather Service initialized")

    def get_current_weather(self, location: str) -> dict:
        """Fetch current weather for a given location."""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            weather_data = response.json()
            logger.info(f"Weather data retrieved for {location}: {weather_data}")
            return weather_data
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return {"error": "Could not fetch weather data."}
