from datetime import datetime
import requests
from langchain.tools import Tool
from langchain.agents import initialize_agent
from langchain_mistralai.chat_models import ChatMistralAI
import pytz

def get_current_time(area=None):
    """Get current time for a specific area or default to UTC"""
    try:
        if area:
            timezone = pytz.timezone(area)
            time = datetime.now(timezone)
            return f"Current time in {area}: {time.strftime('%I:%M:%S %p %Z')}"
        return f"Current UTC time: {datetime.now(pytz.UTC).strftime('%I:%M:%S %p %Z')}"
    except pytz.exceptions.UnknownTimeZoneError:
        return "Please provide a valid timezone (e.g., 'Asia/Kolkata', 'Europe/London')"

def get_weather(city):
    """Get weather information using OpenWeatherMap API with enhanced error handling"""
    API_KEY = "9b5e1760099f0979a39a7ab6f6ef77bc"
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    try:
        # Standardize city input
        city = city.strip()
        if ',' not in city:
            city = f"{city},GB"  # Default to GB if no country specified
        
        # API request with timeout and validation
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Validate response data
        if data.get('cod') != 200:
            return f"Error: {data.get('message', 'Unknown error')}"
        
        # Safe data extraction with defaults
        weather_info = {
            'name': data.get('name', city),
            'country': data.get('sys', {}).get('country', 'Unknown'),
            'temp': data.get('main', {}).get('temp', 'N/A'),
            'feels_like': data.get('main', {}).get('feels_like', 'N/A'),
            'humidity': data.get('main', {}).get('humidity', 'N/A'),
            'wind_speed': data.get('wind', {}).get('speed', 'N/A'),
            'clouds': data.get('clouds', {}).get('all', 'N/A'),
            'description': data.get('weather', [{'description': 'N/A'}])[0]['description']
        }
        
        # Format response with validated data
        return (
            f"Weather in {weather_info['name']}, {weather_info['country']}:\n"
            f"🌡️ Temperature: {weather_info['temp']}°C\n"
            f"🌡️ Feels like: {weather_info['feels_like']}°C\n"
            f"💧 Humidity: {weather_info['humidity']}%\n"
            f"💨 Wind: {weather_info['wind_speed']} m/s\n"
            f"☁️ Clouds: {weather_info['clouds']}%\n"
            f"📝 Status: {weather_info['description']}"
        )
    
    except requests.Timeout:
        return "Error: Weather service timeout. Please try again."
    except requests.RequestException as e:
        return f"Error connecting to weather service: {str(e)}"
    except Exception as e:
        return f"Unexpected error for {city}: {str(e)}"

def create_agent(api_key):
    """Initialize and return Mistral agent with tools"""
    if not api_key:
        return None
        
    try:
        llm = ChatMistralAI(
            model="mistral-small-latest",
            temperature=0.3,
            mistral_api_key=api_key
        )
        
        tools = [
            Tool(
                name="TimeTool",
                func=get_current_time,
                description="Get current time for a timezone. Input: timezone name (e.g., 'Asia/Kolkata')"
            ),
            Tool(
                name="WeatherTool",
                func=get_weather,
                description="Get weather for a city. Input format: 'city,country' (e.g., 'London,GB')"
            )
        ]
        
        return initialize_agent(
            tools=tools,
            llm=llm,
            agent="zero-shot-react-description",
            verbose=True,
            handle_parsing_errors=True,
            system_message="You are a helpful assistant. Use TimeTool for time and WeatherTool for weather queries."
        )
    except Exception as e:
        raise Exception(f"Error initializing agent: {str(e)}")