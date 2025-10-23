import asyncio
import json
import aiohttp

async def get_weather_forecast(latitude, longitude):
    point_url = f"https://api.weather.gov/points/{latitude},{longitude}"
    
    async with aiohttp.ClientSession() as session:
        # Get the forecast URL from the points endpoint
        async with session.get(point_url) as response:
            if response.status != 200:
                print(f"Error getting point data: HTTP {response.status}")
                return None
            data = await response.json()
            forecast_url = data['properties']['forecast']
        
        # Get the actual forecast data
        async with session.get(forecast_url) as forecast_response:
            if forecast_response.status != 200:
                print(f"Error getting forecast data: HTTP {forecast_response.status}")
                return None
            forecast_data = await forecast_response.json()
            return forecast_data['properties']['periods']

async def main():
    latitude, longitude = 37.8771, -122.1797  # Orinda, California
    
    try:
        periods = await get_weather_forecast(latitude, longitude)
        
        if periods is None:
            print("Failed to get weather data")
            return

        # Show only today's periods (usually first 2: day and night, or just current)
        today_periods = periods[:1]

        for period in today_periods:
            if 'detailedForecast' in period and period['detailedForecast']:
                return period['detailedForecast']
            
            
    except Exception as e:
        print(f"An error occurred: {e}")




