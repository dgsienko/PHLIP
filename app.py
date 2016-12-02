import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flask.ext.mysql import MySQL
import flask.ext.login as flask_login

import os
import requests
import json


mysql = MySQL()
app = Flask(__name__)
app.secret_key = 

key = config.weatherKey

#These will need to be changed according to your creditionalsb
app.config['MYSQL_DATABASE_USER'] = config.dbUser
app.config['MYSQL_DATABASE_PASSWORD'] = config.dbPass
app.config['MYSQL_DATABASE_DB'] = config.dbName
app.config['MYSQL_DATABASE_HOST'] = config.dbHost
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


def getLocations():
	query = "select city,state from locations"
	cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def getUsersLocation(user_id):
	query = "select lid from users where user_id = '{0}'"
	cursor = conn.cursor()
    cursor.execute(query.format(user_id))
    return cursor.fetchone()[0]

def getLocation(lid):
	query = "select city,state from locations where lid = '{0}'"
	cursor = conn.cursor()
    cursor.execute(query.format(lid))
    return cursor.fetchone()[0]

def location_exists(city,state):
	query = "select * from locations where city='{0}' and state='{1}'"
	cursor = conn.cursor()
    cursor.execute(query.format(city,state))
    return (cursor.rowcount > 0)

def get_lid(city,state):
	query = "select lid from locations where city='{0}' and state='{1}'"
	cursor = conn.cursor()
    cursor.execute(query.format(city,state))
    return cursor.fetchone()[0]

def getMoon(lid):
	city,state = getLocation(lid)
	req = requests.get("http://api.wunderground.com/api/" + key + "/astronomy/q/"  + state +  "/" + city + ".json").content
	parsed = json.loads(req)
	return [ parsed['moon_phase']['sunrise']['hour'], parsed['moon_phase']['sunrise']['minute'], parsed['moon_phase']['sunset']['hour'], parsed['moon_phase']['sunset']['minute'], lid ]

def getTemp(lid):
	city,state = getLocation(lid)
	req = requests.get("http://api.wunderground.com/api/" + key + "/geolookup/conditions/q/"  + state +  "/" + city + ".json").content
	parsed = json.loads(req)
	return parsed['current_observation']['temp_f']

def setMoon(sunriseH,sunriseM,sunsetH,sunsetM,lid):
	query1 = "delete from current_conditions where lid='{0}'"
	cursor = conn.cursor()
    cursor.execute(query1.format(lid))
    conn.commit()

    query2 = "insert into current_conditions (sunrise_hour, sunrise_minute, sunset_hour, sunset_minute,lid) VALUES ('{0}','{1}','{2}','{3}', '{4}')"
    cursor.execute(query2.format(getMoon()))
    conn.commit()

def setTemp(temp, lid):
	query = "update current_conditions set temp='{0}' where lid='{1}'"
	cursor = conn.cursor()
    cursor.execute(query.format(temp,lid))
    conn.commit()

def create_alert():
	return 1

def run_alerts():
	return 1

def get_alerts():
	return 1


def create_location(city,state):
	query = "insert into locations (city,state) VALUES ('{0}','{1}')"
	cursor = conn.cursor()
    cursor.execute(query.format(city,state))
    conn.commit()

def create_lightEffect(type,length,color):
	return 1

def compare_date(dt,hour,minute):
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
