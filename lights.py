import os
import time
import random



def reset():
	os.system('hue lights all white')
	print('reset lights')
	return 1

def setColor(color):
	os.system('hue lights all ' + str(color).lower())
	print('hue lights all ' + str(color).lower())
	return 1

def setColor_v2(plan_sec,color_ready,song_ready):
	color_ready.set() 
	song_ready.wait()
	for i in range(1,len(plan_sec)):
		os.system('hue lights all ' + randomHex())
		time.sleep(plan_sec[i]-plan_sec[i-1])


def flash(color):
	setColor(color)
	os.system('hue lights all alert')
	print('flashing lights')
	time.sleep(15)
	reset()
	return 1

def onDuration(color,sec):
	sec = int(sec)
	if(sec == -1):
		setColor(color)
		return 1
	else:
		setColor(color)
		time.sleep(sec)
		reset()
		return 1

def cycleDuration(color, sec):
	sec = int(sec)
	if(sec == -1):
		setColor(color)
	else:
		setColor(color)
		os.system('hue lights all colorloop')
		print('cycling colors')
		time.sleep(sec)
		reset()
	return 1



# https://pythonjunkie.wordpress.com/2012/07/19/convert-hex-color-values-to-rgb-in-python/
def hex_to_rgb(value):
	value = value.lstrip('#')
	lv = len(value)
	return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))

def rgb_to_hex(rgb):
	return '%02x%02x%02x' % rgb

def randomHex():
    	hexVal = ["0000FF","FF0000","800080","00FFEC","00EA00","E6ff07","FFAA00","6201B7","FF02E1","188DF9"]
    	choice = random.choice(hexVal)
    	return choice



