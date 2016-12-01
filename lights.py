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

def cycleDuration(sec):
	os.system('hue lights all colorloop')
	time.sleep(sec)
	os.system('hue lights reset')
	return 1