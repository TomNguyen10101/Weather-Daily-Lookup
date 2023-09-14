from flask import Flask, render_template
from weather import WeatherInfo
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timedelta

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class LocationInfo(db.Model):
    location_name = db.Column("location_name", db.String(100), primary_key=True, nullable=False)
    lat = db.Column("lat", db.Integer)
    lon = db.Column("lon", db.Integer)
    timezone = db.Column("timezone", db.String(100))
    tempC = db.Column("temp_in_c", db.Float)
    tempF = db.Column("temp_in_f", db.Float)
    feels_like_c = db.Column("feels_like_c", db.Float)
    feels_like_f = db.Column("feels_like_f", db.Float)
    pressure = db.Column("pressure", db.Float)
    humidity = db.Column("humidity",db.Float)
    windSpeed = db.Column("wind_speed",db.Float)
    description = db.Column("description", db.String(100))
    lastUpdate = db.Column("last_update", db.DateTime)

    def __init__(self, name, lat, lon, timezone, tempC, tempF, feelsLikeC, feelsLikeF, pressure, humidity, windSpeed, description, lastUpdate):
        self.location_name = name
        self.lat = lat
        self.lon = lon
        self.timezone =  timezone
        self.tempC = tempC
        self.tempF = tempF
        self.feels_like_c = feelsLikeC
        self.feels_like_f = feelsLikeF
        self.pressure = pressure
        self.humidity = humidity
        self.windSpeed = windSpeed
        self.description = description
        self.lastUpdate = lastUpdate


@app.route("/")
def homepage():
    return render_template("homepage.html")



@app.route('/weather/<location>')
def weatherpage(location):
    lowercase_location = location.lower()

    # Check if the location is already in the database
    # -> YES, check the last update time -> if later than 1 hour, retrieve the lat, lon then do the API call
    #                                    -> if not, retrieve info then display

    foundLocation = LocationInfo.query.filter_by(location_name=lowercase_location).first()
    print(foundLocation)
    if foundLocation:
        if datetime.now() < (foundLocation.lastUpdate + timedelta(hours=1)):
            displayInfo = [foundLocation.timezone, foundLocation.tempC, foundLocation.feels_like_c, foundLocation.pressure, 
                        foundLocation.humidity, foundLocation.windSpeed, foundLocation.description]
        else:
            cityWeather = WeatherInfo(foundLocation.location_name, foundLocation.lat, foundLocation.lon)
            cityWeather.GetInfo()
            displayInfo = [cityWeather.timezone, cityWeather.tempC,cityWeather.feelsLikeC,cityWeather.pressure, 
                        cityWeather.humidity, cityWeather.windSpeed, cityWeather.weatherDescription]


            # Modify the object in database with new info
            foundLocation.tempC = cityWeather.tempC
            foundLocation.tempF = cityWeather.tempF
            foundLocation.feels_like_c = cityWeather.feelsLikeC
            foundLocation.feels_like_f = cityWeather.feelsLikeF
            foundLocation.pressure = cityWeather.pressure
            foundLocation.humidity = cityWeather.humidity
            foundLocation.windSpeed = cityWeather.windSpeed
            foundLocation.description = cityWeather.weatherDescription
            foundLocation.lastUpdate = datetime.now()

            db.session.commit()
       
    
    # If not in the database then you would find the info about the location and return it
    else:
        print("Adding new location to database ...")
        
        cityWeather = WeatherInfo(location)
        cityWeather.GetInfo()
        displayInfo = [cityWeather.timezone, cityWeather.tempC,cityWeather.feelsLikeC,cityWeather.pressure, 
                        cityWeather.humidity, cityWeather.windSpeed, cityWeather.weatherDescription]
    
        # Add to the database and commit changes
        newLocation = LocationInfo(lowercase_location, cityWeather.lat, cityWeather.lon, cityWeather.timezone, cityWeather.tempC,
                                   cityWeather.tempF, cityWeather.feelsLikeC, cityWeather.feelsLikeF, cityWeather.pressure, 
                                   cityWeather.humidity, cityWeather.windSpeed, cityWeather.weatherDescription, datetime.now())
          
        db.session.add(newLocation)
        db.session.commit()

    return render_template("index.html", location=location.capitalize(),timezone=displayInfo[0],temp=displayInfo[1],feelslike=displayInfo[2],
                           pressure=displayInfo[3],humidity=displayInfo[4],windspeed=displayInfo[5],description=displayInfo[6])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=8000)


