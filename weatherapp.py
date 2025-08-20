#imports
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

#getting latitude and longitude for city
def get_coords(city):
    url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json"
    headers = {
        "User-Agent": "python_weather_app(user_email)"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data['lat']), float(data['lon'])
    else:
        return None, None
    
#using lat/lon to pull gridpoints from weather.gov
def gridpoints(lat, lon):
    url = f"https://api.weather.gov/points/{lat},{lon}"
    response = requests.get(url)
    if response.status_code == 200 and 'properties' in response.json():
        data = response.json()
        gridId = data['properties']['gridId']
        gridX = data['properties']['gridX']
        gridY = data['properties']['gridY']
        return gridId, gridX, gridY
    else:
        return None, None, None

#gridpoints to get weather data strings
def forecast(gridId, gridX, gridY):
    url = f"https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        periods = data['properties']['periods']
        forecast = periods[0]
        return f"{forecast['name']}: {forecast['temperature']}°{forecast['temperatureUnit']} - {forecast['detailedForecast']}"
    else:
        return "Could not get forecast data."

#Flask routing

@app.route("/")
def home():
    return render_template_string("""
        <h1>Weather App</h1>
        <form action="/weather" method="get">
            <input name="city" placeholder="Enter US city">
            <input type="submit" value="Get Weather">
        </form>
    """)

@app.route("/weather")
def weather():
    city = request.args.get("city")
    if not city:
        return "Please provide a city."
    
    lat, lon = get_coords(city)
    if lat is None or lon is None:
        return f"City '{city}' not found."

    gridId, gridX, gridY = gridpoints(lat, lon)
    if gridId is None:
        return "Could not find gridpoint."
    
    weather_forecast = forecast(gridId, gridX, gridY)
    return f"<h2>Weather for {city}</h2><p>{weather_forecast}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)





