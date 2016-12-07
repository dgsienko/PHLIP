import os
import time
import random

def reset():
	os.system('hue lights all clear')
	os.system('hue lights all white')
	print('reset lights')
	return 1

def setColor(color):
        #Sets all lights to input color
	os.system('hue lights all ' + str(color).lower())
	print('hue lights all ' + str(color).lower())
	return 1

def setColor_v2(plan_sec,color_ready,song_ready):
        #V2 sets colors at given time intervals given input plan (in seconds)
	color_ready.set() 
	song_ready.wait()
	for i in range(1,len(plan_sec)):
		os.system('hue lights all ' + randomHex())
		time.sleep(plan_sec[i]-plan_sec[i-1])

def flash(color):
        #Flashes lights at input color
	setColor(color)
	os.system('hue lights all alert')
	print('flashing lights')
	time.sleep(15)
	reset()
	return 1

def onDuration(color,sec):
        #Sets color for some input duration of time, then resets
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
        #cycles lights (solid color or color loop) for some input duration
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
        #Converts hex to rgb
	value = value.lstrip('#')
	lv = len(value)
	return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))

def rgb_to_hex(rgb):
        #Converts rgb to hex
	return '%02x%02x%02x' % rgb

def randomHex():
        #Returns random hex value from list of 10 colors (in hex)
    	hexVal = ["0000FF","FF0000","800080","00FFEC","00EA00","E6ff07","FFAA00","6201B7","FF02E1","188DF9"]
    	choice = random.choice(hexVal)
    	return choice

def invertHex_primer(hexnum):
        #Primer to invert a hex number
        inverse = hex(abs(int(hexnum, 16) - 255))[2:] 
        #If the number is single digit add a preceding zero
        if len(inverse) == 1: 
        	inverse = '0'+inverse
        return inverse
    
def hexInvert_main(hexnum):
        #Define an empty string for new hex
        inverse = "" 
        #If the input hex is RGB
        if len(hexnum) == 6: 
                R = hexnum[:2]
                G = hexnum[2:4]
                B = hexnum[4:]
        inverse = inverse + invertHex_primer(R)
        inverse = inverse + invertHex_primer(G)
        inverse = inverse + invertHex_primer(B)
        return inverse.upper()
