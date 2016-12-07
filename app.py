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

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger



'''
	<script src="{{ url_for('static', filename='jquery-3.1.1.min.js') }}"></script>
	<script type="text/javascript" src="{{ url_for('static', filename='alerts.js') }}"></script>
'''

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



# def print_date_time():
# 	print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))

# scheduler = BackgroundScheduler()
# scheduler.start()
# scheduler.add_job(
# 	func=print_date_time,
# 	trigger=IntervalTrigger(seconds=5),
# 	id='printing_job',
# 	name='Print date and time every five seconds',
# 	replace_existing=True)
# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())















def get_locations():
	query = "select city,state from locations"
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()

def get_lids():
	query = "select lid from locations"
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


def get_alert(alert_type,alert_sign,alert_temp):
	query = "select alert_id from alerts where alert_type = '{0}' and alert_sign='{1}' and alert_temp='{2}'"
	cursor = conn.cursor()
	cursor.execute(query.format(alert_type,alert_sign,alert_temp))
	if (cursor.rowcount > 0):
		return cursor.fetchone()[0]
	else:
		return -1

def get_display_alerts():
	query = 'select u.email, a.alert_type, a.alert_sign, a.alert_temp, l.light_type, l.light_color, l.light_length, a.alert_id from users u, alerts a, light_effects l where l.light_id=a.light_id and u.user_id=a.user_id'
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()

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

def get_saved_condition(lid):
	query = "select * from locations where lid = '{0}'"
	cursor = conn.cursor()
	cursor.execute(query.format(lid))
	return cursor.fetchone()[0]

def run_alerts(user_id):
	lid = get_users_location(user_id)
	condition_id,dt,_,sunrise_hour,sunrise_minute,sunset_hour,sunset_minute,current_temp = get_saved_condition(lid)
	newTemp = get_temp(lid)
	temp_alerts = get_temp_alerts()
	for temp_alert in temp_alerts:
		if (should_temp_rule(current_temp,newTemp,temp_alert[4],temp_alert[5])):
			run_lights(temp_alert[1])


	set_temp(newTemp,lid)
	return 1

def should_temp_rule(prev_temp, new_temp, rule_temp, rule_sign):
	if(rule_sign == 1):
		return (new_temp > rule_temp and prev_temp < rule_temp)
	else:
		return (new_temp < rule_temp and prev_temp > rule_temp)
			


def run_once_a_day():
	locations = get_locations()
	for location in locations:
		set_moon(get_moon(location[0],location[1]))



def should_sun_rule(lid):
	_,dt,_,sunrise_hour,sunrise_minute,sunset_hour,sunset_minute,current_temp = get_saved_condition(lid)
	curr_hr = datetime.datetime.now().time().hour
	curr_min = datetime.datetime.now().time().minute
	if (within_range_after(config.updateSpeed, sunrise_hour,sunrise_minute, curr_hr, curr_min)):
		return -1
	if (within_range_after(config.updateSpeed, sunset_hour,sunset_minute, curr_hr, curr_min)):
		return 1
	else:
		return 0

def run_sun_rule(sign):
	if(sign != 1 or sign != -1):
		return -1
	_,light_id,user_id,alert_type,alert_sign,alert_temp = get_sun_alerts(sign)
	if(should_sun_rule(get_users_location(user_id))):
		run_lights(light_id)
	
def run_lights(light_id):
	_,light_type,color,length = get_light_effect(light_id)
	if(light_type == 'flash'):
		l.flash(color)
	elif(light_type == 'loop'):
		l.cycleDuration(color,length)
	else:
		l.onDuration(color,length)

def run_lights(light_type, color, length):
	print('run lights with params:',light_type,',',color,',',length)
	if(light_type == 'flash'):
		l.flash(color)
	elif(light_type == 'loop'):
		l.cycleDuration(color,length)
	else:
		l.onDuration(color,length)


def get_light_effect(light_id):
	query="select * from light_effects where light_id='{0}'"
	cursor = conn.cursor()
	cursor.execute(query.format(light_id))
	return cursor.fetchone()[0]

def get_alerts():
	query="select * from alerts"
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()

def get_sun_alert(sign):
	query="select * from alerts where alert_type='sun' and sign='{0}' LIMIT 1"
	cursor = conn.cursor()
	cursor.execute(query.format(sign))
	return cursor.fetchone()[0]

def get_temp_alerts():
	query="select * from alerts where alert_type='temp'"
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()


def create_location(city,state):
	query = "insert into locations (city,state) VALUES ('{0}','{1}')"
	cursor = conn.cursor()
	cursor.execute(query.format(city.upper(),state.upper()))
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
	cursor.execute(query.format(light_type,color,length))
	conn.commit()

def compare_date(dt,hour,minute):
	return 1

def convertSQLDateTimeToTimestamp(value):
    return time.mktime(time.strptime(value, '%Y-%m-%d %H:%M:%S'))


def within_range_after(range_after,curr_hr,curr_min,new_hr,new_min):
	if(curr_hr == new_hr):
		return (curr_min+range_after > new_min)
	elif(curr_hr+1 == new_hr):
		return ((curr_min+range_after)%60 > new_min)
	else:
		return False


def exists_users():
	query="select * from users"
	cursor=conn.cursor()
	cursor.execute(query)
	return (cursor.rowcount > 0)


def get_settings():
	query='select s.update_speed, s.new_users, s.weather_key, s.music_key, l.city, l.state from settings s, locations l where l.lid = s.lid'
	cursor=conn.cursor()
	cursor.execute(query)
	return cursor.fetchone()

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

def update_settings(update_speed,new_users,weather_key,music_key,city,state):
	lid = get_location(city,state)
	if(lid == -1):
		create_location(city,state)
		lid = get_location(city,state)
	query="update settings set update_speed={0} new_users={1} weather_key='{2}' music_key='{3}' lid='{4}'"
	cursor = conn.cursor()
	cursor.execute(query.format(update_speed,new_users,weather_key,music_key,lid))
	cursor.commit()

def default_settings():
	query1 = "delete from settings"
	query2 = "insert into settings(update_speed,new_users,weather_key,music_key,lid) values(5,1,'weather_key','music_key',1);"
	cursor = conn.cursor()
	cursor.execute(query1)
	cursor.commit()
	cursor.execute(query2)
	cursor.commit()



# Use this to check if a email has already been registered
def isEmailUnique(email):
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM users WHERE email = '{0}'".format(email)): 
		# This means there are greater than zero entries with that email
		return False
	else:
		return True

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM users WHERE email = '{0}'".format(email))
	if(cursor.rowcount > 0):
		return cursor.fetchone()[0]
	else:
		return -1


def delete_alert(alert_id):
	query="delete from alerts where alert_id={0}"
	cursor = conn.cursor()
	cursor.execute(query.format(alert_id))
	conn.commit()



def allow_new_users():
	query="select new_users from settings;"
	cursor = conn.cursor()
	cursor.execute(query)
	if(cursor.rowcount > 0):
		return (cursor.fetchone()[0] == 1) 
	else:
		return True



#
#
# different routes
#
#

#---#

@app.route('/', methods=['GET'])
def index():
	if(not(exists_users())):
		return redirect('/register')
	elif(flask_login.current_user.is_anonymous):
		return redirect('/login')
	else:
		return redirect('/home')

#---#

@app.route("/login", methods=['GET'])
def login():
	return render_template('login.html')  
    

@app.route("/login", methods=['POST'])
def login_post():
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()     #check if email is registered     
	if cursor.execute("SELECT password FROM users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		print (data)
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect('/home') #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
	</br><a href='/register'>or make an account</a>"
	return render_template('login.html', supress='True')

#---#

@app.route("/testlights", methods=['GET'])
@flask_login.login_required
def test_lights_get():
	return redirect('/addrules')


@app.route("/testlights", methods=['POST'])
@flask_login.login_required
def test_lights_post():
	print('/testlights post')
	effect = ''
	color = ''
	length = ''
	try:
		effect = request.form['effect']
		length = int(request.form['length'])
		color = request.form['color']
		
	except:
		print('not all values filled')
		print('effect:',effect,", color:",color,", length:",length)
		return redirect('/addrules')
	run_lights(effect,color,length)
	return redirect('/addrules')

#---#


@app.route("/deletealert", methods=['GET'])
@flask_login.login_required
def delete_alert_get():
	return redirect('/addrules')


@app.route("/deletealert", methods=['POST'])
@flask_login.login_required
def delete_alert_post():
	print('/delete alert post')
	effect = ''
	color = ''
	length = ''
	try:
		alert_id = int(request.form['alert_id'])
		
	except:
		print('Bad Values.')
		print('alert_id:',alert_id)
		return redirect('/addrules')
	delete_alert(alert_id)
	return redirect('/addrules')

#---#


@app.route("/home", methods=['GET'])
@flask_login.login_required
def home():
	return render_template('home.html', alert=get_display_alerts())


#---#

@app.route("/logout", methods=['GET'])
def logout():
	flask_login.logout_user()
	return redirect('/')


#---#

@app.route("/addrules", methods=['GET'])
@flask_login.login_required
def addrules():
	return render_template('alerts.html', alerts=get_display_alerts())


@app.route("/addrules", methods=['POST'])
@flask_login.login_required
def addrules_post():
	try:
		alert_type=request.form['alert_type'] # sun or temp
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
			alert_sign=int(request.form['tempdrop']) # 1, -1
			alert_temp=int(request.form['tempval']) # string of number
			light_type=request.form['tempeffect'] # flash loop on
			dur=int(request.form['tempduration']) # string of number
			color = request.form['tempcolor'] # string

			print('A',user_id, alert_type, alert_sign, alert_temp, light_type, dur, color)
			create_alert(user_id, alert_type, alert_sign, alert_temp, light_type, dur, color)

		elif(alert_type == 'sun'):
			print('f')
			alert_sign=int(request.form['sundrop']) # 1, -1
			print('g')
			light_type=request.form['suneffect'] # flash loop on
			dur=int(request.form['sunduration']) # string of number
			color = request.form['suncolor'] # string

			print('B',user_id, alert_type, alert_sign, alert_temp, light_type, dur, color)
			create_alert(user_id, alert_type, alert_sign, 0, light_type, dur, color)
			print('ff')
		else:
			print('bad values passed in.')
			return redirect('/addrules', message='Bad Values!')


		
	except:
		print('C',user_id, alert_type, alert_sign, alert_temp, light_type, dur, color)
		print("couldn't find all tokens") # End users won't see this (print statements go to shell)
		return flask.redirect('/addrules')
	return redirect('/addrules')


#---#

@app.route("/setup", methods=['GET'])
@flask_login.login_required
def setup():
	return render_template('setup.html', settings=get_settings())


@app.route("/setup", methods=['POST'])
@flask_login.login_required
def setup_post():

	return redirect('/setup')


#---#

@app.route("/music", methods=['GET'])
@flask_login.login_required
def music():
	audio.mainRun('music/The.Madpix.Project - Liquid Blue.wav',95)
	return render_template('music.html')


@app.route("/music", methods=['POST'])
@flask_login.login_required
def music_post():
	return render_template('music.html')

#---#


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
		email=request.form.get('email')
		password=request.form.get('password')
	except:
		print("couldn't find all tokens") # End users won't see this (print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password) VALUES ('{0}', '{1}')".format(email, password)))
		conn.commit()
		user = User()
		user.id = email
		flask_login.login_user(user)
		return redirect('/')
	return redirect('/register')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect('/')


#---#

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
