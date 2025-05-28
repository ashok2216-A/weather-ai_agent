from datetime import datetime
import requests
import pytz

def get_current_time(area=None):

    try:
        if area:
            timezone = pytz.timezone(area)
            time = datetime.now(timezone)
            return f"Current time in {area}: {time.strftime('%I:%M:%S %p %Z on %Y-%m-%d')}"
        return f"Current UTC time: {datetime.now(pytz.UTC).strftime('%I:%M:%S %p %Z on %Y-%m-%d')}"
    except pytz.exceptions.UnknownTimeZoneError:
        return "Please provide a valid timezone (e.g., 'Asia/Kolkata', 'Europe/London')"

def get_weather(city):

    API_KEY = "9b5e1760099f0979a39a7ab6f6ef77bc"
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    try:
        city = city.strip()
        # Remove default country assignment for better accuracy
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('cod') != 200:
            return f"Error: {data.get('message', 'City not found')}"
        
        weather_info = {
            'name': data.get('name', city), 'country': data.get('sys', {}).get('country', 'Unknown'), 'temp': round(data.get('main', {}).get('temp', 0), 1),
            'feels_like': round(data.get('main', {}).get('feels_like', 0), 1), 'humidity': data.get('main', {}).get('humidity', 0),
            'wind_speed': round(data.get('wind', {}).get('speed', 0), 1), 'clouds': data.get('clouds', {}).get('all', 0),
            'description': data.get('weather', [{'description': 'N/A'}])[0]['description'].title()
        }
        
        return (
            f"Weather in {weather_info['name']}, {weather_info['country']}:\n"
            f"Temperature: {weather_info['temp']}°C (feels like {weather_info['feels_like']}°C)\n"
            f"Humidity: {weather_info['humidity']}%\n"
            f"Wind: {weather_info['wind_speed']} m/s\n"
            f"Clouds: {weather_info['clouds']}%\n"
            f"Condition: {weather_info['description']}"
        )
    
    except requests.Timeout:
        return "Weather service timeout. Please try again."
    except requests.RequestException:
        return "Unable to connect to weather service."
    except Exception as e:
        return f"Error getting weather for {city}. Please check city name."
