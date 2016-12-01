import requests
import json
import config


key = config.weatherKey

city = 'BOSTON'
state = 'MA'


req = requests.get("http://api.wunderground.com/api/" + key + "/astronomy/q/"  + state +  "/" + city + ".json").content
parsed = json.loads(req)
print(parsed['moon_phase']['sunrise']['hour'])
