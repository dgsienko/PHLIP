import requests
import json
import config
import random
import os
import lights
import time
import datetime


dt = datetime.datetime.now().time().hour
print(dt)







key = config.weatherKey

city = 'BOSTON'
state = 'MA'


req = requests.get("http://api.wunderground.com/api/" + key + "/astronomy/q/"  + state +  "/" + city + ".json").content
parsed = json.loads(req)
print(parsed['moon_phase']['sunset']['hour'])









def gen_hex_colour_code():
   return ''.join([random.choice('0123456789ABCDEF') for x in range(6)])

lights = [9,10,11,12,13,14,15,16,17]

while(False):
	os.system( 'hue lights ' + str(random.choice(lights)) + " " + str(gen_hex_colour_code()))
