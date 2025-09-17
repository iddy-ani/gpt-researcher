#!/usr/bin/env python3
"""
Quick test script for weather-info functionality
"""
import asyncio
import sys
import os

# Add the current directory to Python path to import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the weather functions from the weather-info module
# Since the filename has a hyphen, we need to import it differently
import importlib.util
spec = importlib.util.spec_from_file_location("weather_info", "weather-info-completed.py")
weather_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(weather_module)

get_weather = weather_module.get_weather
get_forecast = weather_module.get_forecast
convert_temperature = weather_module.convert_temperature

async def test_weather_functions():
    print("🧪 Testing Weather App Functions\n")
    
    # Test temperature conversion
    print("1. Testing Temperature Conversion:")
    temp_result = await convert_temperature({
        "temperature": 25,
        "from_unit": "celsius",
        "to_unit": "fahrenheit"
    })
    print(temp_result[0]["text"])
    print()
    
    # Test weather (demo mode)
    print("2. Testing Current Weather (Demo Mode):")
    weather_result = await get_weather({
        "location": "London",
        "units": "celsius"
    })
    print(weather_result[0]["text"])
    print()
    
    # Test forecast (demo mode)
    print("3. Testing Weather Forecast (Demo Mode):")
    forecast_result = await get_forecast({
        "location": "New York",
        "days": 3
    })
    print(forecast_result[0]["text"])
    print()
    
    print("✅ All tests completed!")
    print("\n💡 To get real weather data:")
    print("   1. Get a free API key from https://openweathermap.org/api")
    print("   2. Set environment variable: OPENWEATHER_API_KEY=your_api_key")
    print("   3. Run the weather server again")

if __name__ == "__main__":
    asyncio.run(test_weather_functions())