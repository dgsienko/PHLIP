'''
CS 411 Group 4
app.py
Largely prepared by Jacob Bogdanov
Commented by Karan Varindani
'''


## Import Statements
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

import os
import requests
import json
import datetime

import lights as l
import audio
import config


import time
import atexit

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


## Hooks to JavaScript
'''
	<script src="{{ url_for('static', filename='jquery-3.1.1.min.js') }}"></script>
	<script type="text/javascript" src="{{ url_for('static', filename='alerts.js') }}"></script>
'''

## Flask-MySQL Connector
mysql = MySQL()
app = Flask(__name__)
app.secret_key = config.secret_key



## Lookup config file to authenticate database
app.config['MYSQL_DATABASE_USER'] = config.dbUser
app.config['MYSQL_DATABASE_PASSWORD'] = config.dbPass
app.config['MYSQL_DATABASE_DB'] = config.dbName
app.config['MYSQL_DATABASE_HOST'] = config.dbHost
app.config['UPLOAD_FOLDER'] = 'static'
mysql.init_app(app)

## Login code starts here
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()



## Get light settings from the database
def get_settings():
	query='select s.update_speed, s.new_users, s.weather_key, s.music_key, l.city, l.state from settings s, locations l where l.lid = s.lid'
	cursor=conn.cursor()
	cursor.execute(query)
	return cursor.fetchone()

## Get a specific setting from the databased given an input keyword
def get_setting(keyword):
	settings = get_settings()
	if(keyword == 'update_speed'):
		return settings[0]
	elif(keyword == 'new_users'):
		return settings[1]
	elif(keyword == 'weather_key'):
		return settings[2]
	elif(keyword == 'music_key'):
		return settings[3]
	elif(keyword == 'city'):
		return settings[4]
	elif(keyword == 'state'):
		return settings[5]
	else:
		return ''




key = get_setting('weather_key')

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from users") 
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM user WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd 
	return user
###

## Queries the database for a city,state
def get_locations():
	query = "select city,state from locations"
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()

## Queries the database for a location id
def get_lids():
	query = "select lid from locations"
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()

## Queries the database for a location id given a user id
def get_users_location(user_id):
	query = "select lid from users where user_id = '{0}'"
	cursor = conn.cursor()
	cursor.execute(query.format(user_id))
	return cursor.fetchone()[0]

## Queries the database for a city,state given a location id
def get_location(lid):
	query = "select city,state from locations where lid = '{0}'"
	cursor = conn.cursor()
	cursor.execute(query.format(lid))
	return cursor.fetchone()

## Takes a city,state and returns if a city exists in the database
def location_exists(city,state):
	query = "select * from locations where city='{0}' and state='{1}'"
	cursor = conn.cursor()
	cursor.execute(query.format(city,state))
	return (cursor.rowcount > 0)

## Takes a city,state and returns an id number (or -1 if nonexistent)
def get_lid(city,state):
	query = "select lid from locations where city='{0}' and state='{1}'"
	cursor = conn.cursor()
	cursor.execute(query.format(city,state))
	if (cursor.rowcount > 0):
		return cursor.fetchone()[0]
	else:
		return -1

## Takes a location id and returns the sunrise/sunset information
def get_moon(lid):
	city,state = get_location(lid)
	req = requests.get("http://api.wunderground.com/api/" + key + "/astronomy/q/"  + state +  "/" + city + ".json").content
	parsed = json.loads(req)
	return [ parsed['moon_phase']['sunrise']['hour'], parsed['moon_phase']['sunrise']['minute'], parsed['moon_phase']['sunset']['hour'], parsed['moon_phase']['sunset']['minute'], lid ]

## Takes a location id and returns temperature information
def get_temp(lid):
	city,state = getLocation(lid)
	req = requests.get("http://api.wunderground.com/api/" + key + "/geolookup/conditions/q/"  + state +  "/" + city + ".json").content
	parsed = json.loads(req)
	return parsed['current_observation']['temp_f']

## Updates the database with the current sunrise/sunset information
def set_moon(sunriseH,sunriseM,sunsetH,sunsetM,lid):
	query1 = "delete from current_conditions where lid='{0}'"
	cursor = conn.cursor()
	cursor.execute(query1.format(lid))
	conn.commit()

	query2 = "insert into current_conditions (sunrise_hour, sunrise_minute, sunset_hour, sunset_minute,lid) VALUES ('{0}','{1}','{2}','{3}', '{4}')"
	cursor.execute(query2.format(getMoon()))
	conn.commit()

## Updates the database with the current temperature 
def set_temp(temp, lid):
	query = "update current_conditions set temp='{0}' where lid='{1}'"
	cursor = conn.cursor()
	cursor.execute(query.format(temp,lid))
	conn.commit()

## Gets the existing rules from the databse
def get_alert(alert_type,alert_sign,alert_temp):
	query = "select alert_id from alerts where alert_type = '{0}' and alert_sign='{1}' and alert_temp='{2}'"
	cursor = conn.cursor()
	cursor.execute(query.format(alert_type,alert_sign,alert_temp))
	if (cursor.rowcount > 0):
		return cursor.fetchone()[0]
	else:
		return -1

## Returns a table with all existing rules
def get_display_alerts():
	query = 'select u.email, a.alert_type, a.alert_sign, a.alert_temp, l.light_type, l.light_color, l.light_length, a.alert_id from users u, alerts a, light_effects l where l.light_id=a.light_id and u.user_id=a.user_id'
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()

## Create an alert rule based on user input from the HTML
def create_alert(user_id, alert_type, alert_sign, alert_temp, light_type, length, color):
	if(light_type == 'flash'):
		length = 30
	light_id = get_light_id(light_type,length, color)
	print('here')
	if (light_id == -1):
		print('inside if')
		create_lightEffect(light_type,length, color)
		print('created light effect')
		light_id = get_light_id(light_type,length, color)
	
	alert_id = get_alert(alert_type, alert_sign, alert_temp)
	print('alert_id=',alert_id)
	if(alert_id == -1):
		print('inside if')
		print((user_id,light_id,alert_type,alert_sign,alert_temp))
		query = "insert into alerts(user_id,light_id,alert_type,alert_sign,alert_temp) values({0},{1},'{2}',{3},{4})"
		cursor = conn.cursor()
		print(query.format(user_id,light_id,alert_type,alert_sign,alert_temp))
		cursor.execute(query.format(user_id,light_id,alert_type,alert_sign,alert_temp))
		conn.commit()
		print('query finished A')
	else:
		print('inside else')
		query = "update alerts set light_id={0}, user_id={1} where alert_id={2}"
		print(query.format(light_id,user_id,alert_id))
		cursor = conn.cursor()
		cursor.execute(query.format(light_id,user_id,alert_id))
		conn.commit()
		print('query finished B')

## Queries the database for the conditions of a given location id
def get_saved_condition(lid):
	query = "select * from locations where lid = '{0}'"
	cursor = conn.cursor()
	cursor.execute(query.format(lid))
	return cursor.fetchone()[0]

## Runs a defined alert
def run_alerts():
	lid = 1
	condition_id,dt,_,sunrise_hour,sunrise_minute,sunset_hour,sunset_minute,current_temp = get_saved_condition(lid)
	newTemp = get_temp(lid)
	temp_alerts = get_temp_alerts()
	for temp_alert in temp_alerts:
		if (should_temp_rule(current_temp,newTemp,temp_alert[4],temp_alert[5])):
			run_lights(temp_alert[1])


	set_temp(newTemp,lid)
	return 1

## Should a temperature rule run?
def should_temp_rule(prev_temp, new_temp, rule_temp, rule_sign):
	if(rule_sign == 1):
		return (new_temp > rule_temp and prev_temp < rule_temp)
	else:
		return (new_temp < rule_temp and prev_temp > rule_temp)
			

## Checks sunrise/sunset information daily
def run_once_a_day():
	locations = get_locations()
	for location in locations:
		set_moon(get_moon(get_lid(location[0],location[1])))

## Should a sunrise/sunset rule run?
def should_sun_rule(lid):
	_,dt,_,sunrise_hour,sunrise_minute,sunset_hour,sunset_minute,current_temp = get_saved_condition(lid)
	curr_hr = datetime.datetime.now().time().hour
	curr_min = datetime.datetime.now().time().minute
	if (within_range_after(get_setting('update_speed'), sunrise_hour,sunrise_minute, curr_hr, curr_min)):
		return -1
	if (within_range_after(get_setting('update_speed'), sunset_hour,sunset_minute, curr_hr, curr_min)):
		return 1
	else:
		return 0

## If yes (above), run sunrise/sunset rule
def run_sun_rule(sign):
	if(sign != 1 or sign != -1):
		return -1
	_,light_id,user_id,alert_type,alert_sign,alert_temp = get_sun_alerts(sign)
	if(should_sun_rule(get_users_location(user_id))):
		run_lights(light_id)

## Runs lights given a light id	
def run_lights(light_id):
	_,light_type,color,length = get_light_effect(light_id)
	if(light_type == 'flash'):
		l.flash(color)
	elif(light_type == 'loop'):
		l.cycleDuration(color,length)
	else:
		l.onDuration(color,length)

## Runs lights given certain parameters
def run_lights(light_type, color, length):
	print('run lights with params:',light_type,',',color,',',length)
	if(light_type == 'flash'):
		l.flash(color)
	elif(light_type == 'loop'):
		l.cycleDuration(color,length)
	else:
		l.onDuration(color,length)

## Get the effects stored for a given light
def get_light_effect(light_id):
	query="select * from light_effects where light_id='{0}'"
	cursor = conn.cursor()
	cursor.execute(query.format(light_id))
	return cursor.fetchone()[0]

## Get all alert rules
def get_alerts():
	query="select * from alerts"
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()

## Get sunrise/sunset alert rules
def get_sun_alert(sign):
	query="select * from alerts where alert_type='sun' and sign='{0}' LIMIT 1"
	cursor = conn.cursor()
	cursor.execute(query.format(sign))
	return cursor.fetchone()[0]

## Get temperature alert rules
def get_temp_alerts():
	query="select * from alerts where alert_type='temp'"
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()

## Creates a location in the database given a city,state
def create_location(city,state):
	query = "insert into locations (city,state) VALUES ('{0}','{1}')"
	cursor = conn.cursor()
	cursor.execute(query.format(city.upper(),state.upper()))
	conn.commit()

## Gets a light id from the database given some parameters
def get_light_id(light_type,length,color):
	query="select light_id from light_effects where light_type='{0}' and light_length='{1}' and light_color='{2}'"
	cursor = conn.cursor()
	cursor.execute(query.format(light_type,length,color))
	if (cursor.rowcount > 0):
		return cursor.fetchone()[0]
	else:
		return -1

## Creates a light effect in the database given some paramterers
def create_lightEffect(light_type,length,color):
	query="insert into light_effects (light_type, light_color, light_length) values ('{0}','{1}',{2})"
	cursor = conn.cursor()
	cursor.execute(query.format(light_type,color,length))
	conn.commit()



def get_all_lights():
	query="select lamp_id from lights"
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()

def get_lights_by_group_id(group_id):
	query="select lamp_id from light_groups where group_id={0}"
	cursor = conn.cursor()
	cursor.execute(query.format(group_id))
	return cursor.fetchall()

def get_group_names():
	query="select group_name from groups"
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()

def get_group_id_by_name(group_name):
	query="select group_id from groups where group_name={0}"
	cursor = conn.cursor()
	cursor.execute(query.format(group_name))
	return cursor.fetchone()[0]




''' 
def compare_date(dt,hour,minute):
	return 1
'''

## Converts SQL DateTime to a Python timestamp
def convertSQLDateTimeToTimestamp(value):
    return time.mktime(time.strptime(value, '%Y-%m-%d %H:%M:%S'))

## Determines if a rule should be run
def within_range_after(range_after,curr_hr,curr_min,new_hr,new_min):
	if(curr_hr == new_hr):
		return (curr_min+range_after > new_min)
	elif(curr_hr+1 == new_hr):
		return ((curr_min+range_after)%60 > new_min)
	else:
		return False

## Checks if users exist
def exists_users():
	query="select * from users"
	cursor=conn.cursor()
	cursor.execute(query)
	return (cursor.rowcount > 0)



## Update settings in the databse given parameters
def update_settings(update_speed,new_users,weather_key,music_key,city,state):
	lid = get_lid(city,state)
	if(lid == -1):
		create_location(city,state)
		lid = get_lid(city,state)
	query="update settings set update_speed={0}, new_users={1}, weather_key='{2}', music_key='{3}', lid={4}"
	print(query.format(update_speed,new_users,weather_key,music_key,lid))
	cursor = conn.cursor()
	cursor.execute(query.format(update_speed,new_users,weather_key,music_key,lid))
	conn.commit()

## Returns settings back to default in the database
def default_settings():
	query1 = "delete from settings"
	query2 = "insert into settings(update_speed,new_users,weather_key,music_key,lid) values(5,1,'weather_key','music_key',1);"
	cursor = conn.cursor()
	cursor.execute(query1)
	conn.commit()
	cursor.execute(query2)
	conn.commit()



## Checks if an email has already been registered
def isEmailUnique(email):
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM users WHERE email = '{0}'".format(email)): 
		## There are greater than zero entries with that email
		return False
	else:
		return True

## Returns a user id given an email
def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM users WHERE email = '{0}'".format(email))
	if(cursor.rowcount > 0):
		return cursor.fetchone()[0]
	else:
		return -1

## Deletes an alert from the database given an alert id
def delete_alert(alert_id):
	query="delete from alerts where alert_id={0}"
	cursor = conn.cursor()
	cursor.execute(query.format(alert_id))
	conn.commit()

## Allow new users to register and update settings (or stop new users)
def allow_new_users():
	query="select new_users from settings;"
	cursor = conn.cursor()
	cursor.execute(query)
	if(cursor.rowcount > 0):
		return (cursor.fetchone()[0] == 1) 
	else:
		return True
###

def is_int(num):
	try:
		val = int(num)
	except:
		return False
	return True

def is_str(string):
	try:
		val = str(string)
	except:
		return False
	return True


def validate_int(num):
	try:
		val = int(num)
		return val
	except:
		return 0
	return val


def validate_str(string):
	try:
		val = str(string)
		val = val.replace('<','')
		val = val.replace('>', '')
		return val
	except:
		return ''
	return val



# App routes below

## Route for home
@app.route('/', methods=['GET'])
def index():
	print(get_all_lights())
	if(not(exists_users())):
		return render_template('register.html')
	elif(flask_login.current_user.is_anonymous):
		return render_template('login.html', message="Login to continue")
	else:
		return render_template('home.html', message="Login successful", alerts=get_display_alerts())

## Routes to login
@app.route("/login", methods=['GET'])
def login():
	if(flask_login.current_user.is_anonymous):
		return render_template('login.html') 
	else:
		return redirect('/home')

@app.route("/login", methods=['POST'])
def login_post():
	## The request method is POST (page is recieving data)
	email = validate_str(flask.request.form['email'])
	cursor = conn.cursor()     ## Checks if email is registered     
	if cursor.execute("SELECT password FROM users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		print (data)
		pwd = str(data[0][0] )
		if validate_str(flask.request.form['password']) == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) ## Okay - login in user
			return flask.render_template('home.html', message="Login successful", alerts=get_display_alerts() ) ## Protected is a function defined in this file

	## Information did not match
	return "<a href='/login'>Try again</a>\
	</br><a href='/register'>or make an account</a>"
	return render_template('login.html', supress='True')



## Routes to test the lights
@app.route("/testlights", methods=['GET'])
@flask_login.login_required
def test_lights_get():
	return render_template('alerts.html')


@app.route("/testlights", methods=['POST'])
@flask_login.login_required
def test_lights_post():
	print('/testlights post')
	effect = ''
	color = ''
	length = ''
	try:
		effect = validate_str(request.form['effect'])
		length = validate_int(request.form['length'])
		color = validate_str(request.form['color'])
		
	except:
		print('not all values filled')
		print('effect:',effect,", color:",color,", length:",length)
		return render_template('alerts.html')
	run_lights(effect,color,length)
	return render_template('alerts.html')

@app.route("/lights", methods=['POST'])
@flask_login.login_required
def lights_post():
	print('/lights post')
	color = ''
	try:
		color = validate_str(request.form['color'])
		
	except:
		print('not all values filled')
		print("color:",color)
		return render_template('home.html', message='Failed to update lights!!!', alerts=get_display_alerts())
	run_lights('on',color,-1)
	return render_template('home.html', message='Lights updated!', alerts=get_display_alerts())



## Routes to delete a Weather Alert rule
@app.route("/deletealert", methods=['GET'])
@flask_login.login_required
def delete_alert_get():
	return render_template('alerts.html', message="Rule deleted")


@app.route("/deletealert", methods=['POST'])
@flask_login.login_required
def delete_alert_post():
	print('/delete alert post')
	effect = ''
	color = ''
	length = ''
	try:
		alert_id = validate_int(request.form['alert_id'])
		
	except:
		print('Bad Values.')
		print('alert_id:',alert_id)
		return render_html('alerts.html', message="Rule deleted")
	delete_alert(alert_id)
	return render_html('alerts.html', message="Rule deleted")



## Route to Home
@app.route("/home", methods=['GET'])
@flask_login.login_required
def home():
	return render_template('home.html', alerts=get_display_alerts())


## Route to logout
@app.route("/logout", methods=['GET'])
def logout():
	flask_login.logout_user()
	return render_template('login.html', message="Successfully logged out")


## Routes to the Add Rules page
@app.route("/addrules", methods=['GET'])
@flask_login.login_required
def addrules():
	return render_template('alerts.html', alerts=get_display_alerts())


@app.route("/addrules", methods=['POST'])
@flask_login.login_required
def addrules_post():
	try:
		alert_type=validate_str(request.form['alert_type']) # sun or temp
		alert_sign = '-'
		light_type = 0
		light_type= '-'
		dur= '-'
		color= '-'
		alert_temp=0
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		print('d')

		if(alert_type == 'temp'):
			print('e')
			alert_sign=validate_int(request.form['tempdrop']) # 1, -1
			alert_temp=validate_int(request.form['tempval']) # string of number
			light_type=validate_str(request.form['tempeffect']) # flash loop on
			dur=validate_int(request.form['tempduration']) # string of number
			color = validate_str(request.form['tempcolor']) # string

			print('A',user_id, alert_type, alert_sign, alert_temp, light_type, dur, color)
			create_alert(user_id, alert_type, alert_sign, alert_temp, light_type, dur, color)

		elif(alert_type == 'sun'):
			print('f')
			alert_sign=validate_int(request.form['sundrop']) # 1, -1
			print('g')
			light_type=validate_str(request.form['suneffect']) ## Flash loop on
			dur=validate_int(request.form['sunduration']) ## String of number
			color = validate_str(request.form['suncolor']) ## String

			print('B',user_id, alert_type, alert_sign, alert_temp, light_type, dur, color)
			create_alert(user_id, alert_type, alert_sign, 0, light_type, dur, color)
			print('ff')
		else:
			print('bad values passed in.')
			return render_template('alerts.html', message='Bad Values!')


		
	except:
		print('C',user_id, alert_type, alert_sign, alert_temp, light_type, dur, color)
		print("couldn't find all tokens") # End users won't see this (print statements go to shell)
		return flask.render_template('alerts.html', alerts=get_display_alerts())
	return flask.render_template('alerts.html', alerts=get_display_alerts())



## Routes to the website settings
@app.route("/setup", methods=['GET'])
@flask_login.login_required
def setup():
	return render_template('setup.html', settings=get_settings())


@app.route("/setup", methods=['POST'])
@flask_login.login_required
def setup_post():
	try:
		weather_key=validate_str(request.form.get('weather_key'))
		music_key=validate_str(request.form.get('music_key'))
		update_speed=validate_str(request.form.get('update_speed'))
		city=validate_str(request.form.get('city'))
		state=validate_str(request.form.get('state'))
		new_users=-1
		if(validate_str(request.form.get('new_users'))):
			new_users=1


	except:
		print('PROBLEM:: ' , weather_key,',',music_key,',',update_speed,',',city,',',state,',',new_users)
		return flask.render_template('setup.html')
	print('CORRECT:: ' , weather_key,',',music_key,',',update_speed,',',city,',',state,',',new_users)
	update_settings(update_speed,new_users,weather_key,music_key,city,state)
	return render_template('setup.html', settings=get_settings(), message='Successfully update settings!')



## Routes to the Audio Visualizer
@app.route("/music", methods=['GET'])
@flask_login.login_required
def music():
	#audio.mainRun('music/The.Madpix.Project - Liquid Blue.wav',95)
	return render_template('music.html', stage1=True)



# @app.route("/playmusic", methods=['GET'])
# @flask_login.login_required
# def play_music():
# 	#audio.mainRun('music/The.Madpix.Project - Liquid Blue.wav',95)
# 	return render_template('music.html')


@app.route("/forcetempupdate", methods=['GET'])
@flask_login.login_required
def force_temp_update():
	lids = get_lids()
	for lid in lids:
		set_temp(get_temp(lid),lid)
	return redirect('/')

@app.route("/forcemoonupdate", methods=['GET'])
@flask_login.login_required
def force_moon_update():
	lids = get_lids()
	print(lids)
	for lid in lids:
		set_moon(get_moon(lid))
	return redirect('/')


@app.route("/listmusic", methods=['POST'])
@flask_login.login_required
def list_music_post():
	try:
		artist=validate_str(request.form.get('artist'))
	except:
		print('invalid params')
		return render_template('music.html')
	print(artist, get_setting('music_key'))
	song_list,artist_json = audio.get_song_list(get_setting('music_key'),artist)
	return render_template('listmusic.html', artist=artist, song_list=song_list)

@app.route("/playmusic", methods=['POST'])
@flask_login.login_required
def play_music_post():
	print('post to playmusic')
	try:
		print('get song name')
		song_name=validate_str(request.form.get('song_name'))
		artist_name=validate_str(request.form.get('artist'))
	except:
		print('invalid params')
		return render_template('music.html')
	print(song_name)
	fname = audio.get_song(get_setting('music_key'),song_name,artist_name)
	#audio.mainRun(fname,95)
	os.system('python3 audio.py '+ fname)
	return render_template('playmusic.html' )


## Methods to handle registering users
@app.route("/register", methods=['GET'])
def register():
	if(allow_new_users()):
		return render_template('register.html', supress='True')
	else:
		return '''
			<h2 class='error'> You are no longer allowed to register for this site. </h2>
			'''

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=validate_str(request.form.get('email'))
		password=validate_str(request.form.get('password'))
	except:
		print("couldn't find all tokens") # End users won't see this (print statements go to shell)
		return render_template('register.html')
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO users (email, password) VALUES ('{0}', '{1}')".format(email, password)))
		conn.commit()
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('home.html', message="Logged in", alerts=get_display_alerts())
	return render_template('/register', message="Try again")

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('login.html')
###



sched = BlockingScheduler()

sched.add_job(run_once_a_day(), 'cron', month='1-12', day='1-31', hour='1', minute='01')

sched.add_job(
    func=run_alerts(),
    trigger=IntervalTrigger(minutes=get_setting('update_speed')),
    id='getTemp',
    name='get temp every X min',
    replace_existing=True)
sched.start()


## Allows you to run 'python app.py' instead of exporting FLASK_APP
if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0') ## Host '0.0.0.0' so that it projects on the network 