import os
import time



def flash(color):
	os.system('hue lights all ' + color.lower())
	os.system('hue lights all alert')
	return 1

def onDuration(color,sec):
	os.system('hue lights all ' + color.lower())
	time.sleep(sec)
	os.system('hue lights reset')
	return 1

def setColor(color):
	os.system('hue lights all ' + color.lower())
	return 1

def cycleDuration(sec):
	os.system('hue lights all colorloop')
	time.sleep(sec)
	os.system('hue lights reset')
	return 1


# https://pythonjunkie.wordpress.com/2012/07/19/convert-hex-color-values-to-rgb-in-python/
def hex_to_rgb(value):
	value = value.lstrip('#')
  	lv = len(value)
   	return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))

def rgb_to_hex(rgb):
	return '%02x%02x%02x' % rgb

