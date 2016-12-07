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

def invertHex(hexNumber):
    #invert a hex number
    inverse = hex(abs(int(hexNumber, 16) - 255))[2:] 
    # if the number is a single digit add a preceding zero
    if len(inverse) == 1: 
        inverse = '0'+inverse
    return inverse
    
def hexInvert(hexCode):
    #define an empty string for our new color code
    inverse = "" 
    # if the code is RGB
    if len(hexCode) == 6: 
        R = hexCode[:2]
        G = hexCode[2:4]
        B = hexCode[4:]
    # if the code is ARGB
    elif len(hexCode) == 8:
        A = hexCode[:2]
        R = hexCode[2:4]
        G = hexCode[4:6]
        B = hexCode[6:]
        # don't invert the alpha channel
        inverse = inverse + A 
    else:
        # do nothing if it is neither length
        return hexCode 
    inverse = inverse + invertHex(R)
    inverse = inverse + invertHex(G)
    inverse = inverse + invertHex(B)
    return inverse



