import requests
from datetime import datetime
import json


API_KEY = "ed10aedbdb2eeb0761de8ebf471afe2c"

class WeatherInfo:
    # Constructor for the class
    def __init__(self, cityName, lat = None, lon = None):
        # location info
        self.lat = lat
        self.lon = lon
        self.cityName = cityName

        # weather info
        self.timezone = ""
        self.tempC = ""
        self.tempF = ""
        self.feelsLikeC = ""
        self.feelsLikeF = ""
        self.pressure = ""
        self.humidity = ""
        self.windSpeed = ""
        self.weatherDescription = ""
        self.lastUpdate = None

    # Checking the time since last update the weather info
    # def CheckTimeUpdate(self) -> bool:
    #     # TO DO: Optimize this updated time comparing
    #     if self.lastUpdate:
    #         newTime = datetime.now()
    #         if newTime > self.lastUpdate:
    #             return True

    #     return False
    
    def GenerateRequest(self, type) -> str:
        # default setting
        limit = 1
        exclude = "minutely,hourly,daily,alerts"

        # default api call:
        # geocoding api: http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={API key}
        # weather api: https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}

        if type == "geo":
            return f"http://api.openweathermap.org/geo/1.0/direct?q={self.cityName}&limit={limit}&appid={API_KEY}"
        else:
            return f"https://api.openweathermap.org/data/3.0/onecall?lat={self.lat}&lon={self.lon}&exclude={exclude}&appid={API_KEY}"

    
    # Getting weather info
    def GetInfo(self):
        if not self.lat or not self.lon:
            geoRequest = self.GenerateRequest("geo")
            r = requests.get(geoRequest)
            getjson = json.loads(r.text)
            self.lat =  getjson[0]["lat"]
            self.lon = getjson[0]["lon"]
        

        weatherRequest = self.GenerateRequest("weather")
        r = requests.get(weatherRequest)
        getjson = json.loads(r.text)
        self.timezone = getjson["timezone"]

        tempVal = getjson["current"]["temp"]
        self.tempC = self.TempConvert("c", tempVal)
        self.tempF = self.TempConvert("f", tempVal)

        feelsLikeVal = getjson["current"]["feels_like"]
        self.feelsLikeC = self.TempConvert("c", feelsLikeVal)
        self.feelsLikeF = self.TempConvert("f", feelsLikeVal)

        self.pressure = getjson["current"]["pressure"]
        self.humidity = getjson["current"]["humidity"]
        self.windSpeed = getjson["current"]["wind_speed"]
        self.weatherDescription = getjson["current"]["weather"][0]["description"]


    # This function mostly likely use for testing
    def PrintInfo(self) -> None:
        print(f"Location: {self.cityName}")
        print(f"Timezone: {self.timezone}")
        print("temp: {:0.2f}ºC, feels like: {:0.2f}ºC".format(self.tempC, self.feelsLikeC))
        print(f"Pressure: {self.pressure} hPA")
        print(f"Humidity: {self.humidity}%")
        print(f"Wind Speed: {self.windSpeed} m/s")
        print(f"Weather Description: {self.weatherDescription}")           

    def TempConvert(self, type, temp) -> None:
        if type == "c":
            return round(temp - 273.15,2)
        elif type == "f":
            return round((temp - 273.15) * 9/5 + 32,2)









