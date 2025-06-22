from langchain_core.tools import tool
import math
import requests
import json
from geopy.geocoders import Nominatim


def nop(reason: str = "Your response to show to the user"):
    return reason

def getTouristEvents(location: str, day: str):
    with open('.\\llm\\agents\\events.json') as f:
        events = json.load(f)
        day_events = events.get(location, {})
        if day in day_events:
          return f"Interesting tourist events or/and activities in {location} on {day}:\n {day_events[day]}"
        return f"{day} is just a normal day at {location}"

def weatherTool(location: str):
    """Get the weather for a city in next 12 hours"""
    if (location == None) or (location == 'null'):
        return None
    app = Nominatim(user_agent="MyTestApp")
    try:
        location: dict = app.geocode(location)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location for city {location}: {e}")
        return None
    if location == None:
        return "Location is not found"
    latitude = location.latitude
    longitude = location.longitude


    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={latitude}&lon={longitude}"
    headers = {"User-Agent": "MyTestApp/0.1"}  # Replace with your app info

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        weather = response.json()
        weather = {
            "location": location.address,
            "meta": weather['properties']['meta'],
            "weather": weather['properties']['timeseries'][0]['data']
        }
        return weather
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# https://python.langchain.com/v0.2/docs/how_to/custom_tools/
@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return round(a * b, 3)

@tool
def solve_quadratic_equation(a: float, b: float, c: float) -> str:
    """ Solve the quadratic equation ax**2 + bx + c = 0."""
    discriminant = b**2 - 4*a*c

    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2*a)
        x2 = (-b - math.sqrt(discriminant)) / (2*a)
        return f"Two distinct real roots: {x1}, {x2}"
    elif discriminant == 0:
        x = -b / (2*a)
        return f"One real root: {x}"
    else:
        real_part = -b / (2*a)
        imaginary_part = math.sqrt(abs(discriminant)) / (2*a)
        return f"Two complex roots: {real_part} + {imaginary_part}i, {real_part} - {imaginary_part}i"