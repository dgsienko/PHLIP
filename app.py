import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

import os
import requests
import json


mysql = MySQL()
app = Flask(__name__)
app.secret_key = config.secret_key

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


def get_locations():
	query = "select city,state from locations"
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()

def get_users_location(user_id):
	query = "select lid from users where user_id = '{0}'"
	cursor = conn.cursor()
	cursor.execute(query.format(user_id))
	return cursor.fetchone()[0]

def get_location(lid):
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
	if (cursor.rowcount > 0):
		return cursor.fetchone()[0]
	else:
		return -1

def get_moon(lid):
	city,state = getLocation(lid)
	req = requests.get("http://api.wunderground.com/api/" + key + "/astronomy/q/"  + state +  "/" + city + ".json").content
	parsed = json.loads(req)
	return [ parsed['moon_phase']['sunrise']['hour'], parsed['moon_phase']['sunrise']['minute'], parsed['moon_phase']['sunset']['hour'], parsed['moon_phase']['sunset']['minute'], lid ]

def get_temp(lid):
	city,state = getLocation(lid)
	req = requests.get("http://api.wunderground.com/api/" + key + "/geolookup/conditions/q/"  + state +  "/" + city + ".json").content
	parsed = json.loads(req)
	return parsed['current_observation']['temp_f']

def set_moon(sunriseH,sunriseM,sunsetH,sunsetM,lid):
	query1 = "delete from current_conditions where lid='{0}'"
	cursor = conn.cursor()
	cursor.execute(query1.format(lid))
	conn.commit()

	query2 = "insert into current_conditions (sunrise_hour, sunrise_minute, sunset_hour, sunset_minute,lid) VALUES ('{0}','{1}','{2}','{3}', '{4}')"
	cursor.execute(query2.format(getMoon()))
	conn.commit()

def set_temp(temp, lid):
	query = "update current_conditions set temp='{0}' where lid='{1}'"
	cursor = conn.cursor()
	cursor.execute(query.format(temp,lid))
	conn.commit()

def create_alert(user_id, alert_type, alert_sign, alert_temp, light_type, length, color):
	light_id = get_light_id(light_type,length, color)
	if (light_id == -1):
		create_lightEffect(light_type,length, color)
		light_id = get_light_id(light_type,length, color)
	query = "insert into alerts (user_id, light_id, alert_type, alert_sign, alert_temp) values ('{0}','{1}','{2}','{3}','{4}')"
	cursor.execute(query.format(user_id,light_id,alert_type,alert_sign,alert_temp))
	cursor.commit()

def run_alerts():
	return 1

def run_once_a_day():
	locations = get_locations()
	for location in locations:
		set_moon(get_moon(location[0],location[1]))

def get_alerts():
	query="select * from alerts"
	cursor.execute(query)
	return cursor.fetchall()



def create_location(city,state):
	query = "insert into locations (city,state) VALUES ('{0}','{1}')"
	cursor = conn.cursor()
	cursor.execute(query.format(city,state))
	conn.commit()

def get_light_id(light_type,length,color):
	query="select light_id from light_effects where light_type='{0}' and light_length='{1}' and light_color='{2}'"
	cursor = conn.cursor()
	cursor.execute(query.format(light_type,length,color))
	if (cursor.rowcount > 0):
		return cursor.fetchone()[0]
	else:
		return -1

def create_lightEffect(light_type,length,color):
	query="insert into light_effects (light_type, light_color, light_length) values ('{0}','{1}',{2})"
	cursor = conn.cursor()
	cursor.execute(query.format(light_type,length,color))
	conn.commit()

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





# Use this to check if a email has already been registered
def isEmailUnique(email):
   cursor = conn.cursor()
   if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
       # This means there are greater than zero entries with that email
       return False
   else:
       return True

@app.route("/register", methods=['POST'])
def register_user():
   try:
       email=request.form.get('email')
       password=request.form.get('password')
       city=request.form.get('city')
       state=request.form.get('state')
   except:
       print "couldn't find all tokens" # End users won't see this (print statements go to shell)
       return flask.redirect(flask.url_for('register'))
   if get_lid(city,state) == -1:
       create_location(city,state)
       get_lid(city,state)
   else:
       lid = get_lid(city,state)
   cursor = conn.cursor()
   test =  isEmailUnique(email)
   if test:
       print cursor.execute("INSERT INTO Users (email, password, lid) VALUES ('{0}', '{1}', '{2}')".format(email, password, lid))
       conn.commit()





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
