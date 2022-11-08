from fastapi import FastAPI
import redis
from numpy import double
from geopy.geocoders import Nominatim
import json, requests
from redis.commands.json.path import Path
import time

app = FastAPI()
r = redis.Redis(decode_responses=True)
locator = Nominatim(user_agent="savannahs_weather_app")

with open("key.txt") as f:
    openweatherkey = f.readline().rstrip()

base_url = "http://api.openweathermap.org/data/2.5/weather?"

# the root page
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/city")
async def city_weather(city_name: str = "Atlanta"):
    try:
        weather_old = r.json().get(city_name)
        if weather_old.dt <= (time.time() - 1800):
            pass
        return weather_old
    except:
        complete_url = base_url + "appid=" + openweatherkey + "&q=" + city_name
        response_j = requests.get(complete_url).json()
        r.json().set(city_name, Path.root_path(), response_j)
        return response_j

@app.get("/loc")
async def location_weather(lon: double = -122.256051, lat: double = 37.820791):
    coord = str(lon) + str(lat)
    h_coord = "coord_" + str(hash(coord))
    try:
        weather_old = r.json().get(h_coord)
        if weather_old.dt <= (time.time() - 1800):
            pass
        return weather_old
    except:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={openweatherkey}"
        response_j = requests.get(url).json()
        r.json().set(h_coord, Path.root_path(), response_j)
        return response_j