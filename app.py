import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flask.ext.mysql import MySQL
import flask.ext.login as flask_login

import os
import requests
import json

import lights as l
import weather as w

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 

key = config.weatherKey

#These will need to be changed according to your creditionalsb
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = config.DBpass
app.config['MYSQL_DATABASE_DB'] = 'group4'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['UPLOAD_FOLDER'] = 'static'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def index_post():
    l.flash('red')
    return render_template('index.html')




'''
weather
	create rule
		each rule has lighting effect (color, effect duration)
	sunrise/sunset
		make 1 api call a day and then schedule something to happen then
	temp above/below
		specify temp and above or below
	forecast for today/tomorrow
		specify today or tomorrow,
		specify which weather effect
		specify time when will run
'''
@app.route('/weather',methods=['GET'])
def weather_get():

	return 'weather'

@app.route('/weather',methods=['POST'])
def weather_post():

	return 'weather'



def getLocation():
	query = "select city,state from locations"
	cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()[0]

def getMoon():
	city, state = getLocation()
	req = requests.get("http://api.wunderground.com/api/" + key + "/astronomy/q/"  + state +  "/" + city + ".json").content
	parsed = json.loads(req)
	return [ parsed['moon_phase']['sunrise']['hour'], parsed['moon_phase']['sunrise']['minute'], parsed['moon_phase']['sunset']['hour'], parsed['moon_phase']['sunset']['minute'] ]

def getTemp():
	city, state = getLocation()
	req = requests.get("http://api.wunderground.com/api/" + key + "/geolookup/conditions/q/"  + state +  "/" + city + ".json").content
	parsed = json.loads(req)
	return parsed['current_observation']['temp_f']

def setMoon(sunriseH,sunriseM,sunsetH,sunsetM):
	query1 = "delete from current_conditions"
	query2 = "insert into current_conditions (sunrise_hour, sunrise_minute, sunset_hour, sunset_minute) VALUES ('{0}','{1}','{2}','{3}')"
	

	cursor = conn.cursor()
    cursor.execute(query1)
    conn.commit()

    cursor.execute(query1.format(getMoon()))
    conn.commit()

def setTemp(temp):
	query = "update current_conditions set temp='{0}'"
	cursor = conn.cursor()
    cursor.execute(query.format(temp))
    conn.commit()

def create_alert(_):
	return 1

def run_alerts():
	return 1

def get_alerts():
	return 1

def create_location():
	return 1

def create_lightEffect(type,length,color):
	return 1



'''
setup
	register user
		username
		password
		location (city/state)
	register hue bridge
		find the bridge
		tell user to press button on bridge
'''
@app.route('/setup',methods=['GET'])
def setup_get():

	return 'setup'

@app.route('/setup',methods=['POST'])
def setup_post():

	return 'setup'



    

# play music
@app.route('/music',methods=['GET'])
def music_get():

	return 'music'

@app.route('/music',methods=['POST'])
def music_post():

	return 'music'









if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
