#Audio Import, Analysis, and Main for Audio Visualization

import lights
import requests
from pydub import AudioSegment
import numpy as np
import scipy.io.wavfile
import pyaudio
import wave
import time
import multiprocessing
import random
import os

def get_song_list(cid,artist_name):
	#Gets list of songs from input artist

	#Make api call and get dictionary of all songs (and data from songs) by the artist
	url = "https://api.jamendo.com/v3.0/tracks/?client_id="+str(cid)+"&artist_name="+artist_name
	response = requests.get(url)
	artist_json = response.json()
    
	#Makes a list of all songs by the artist
	song_list = [artist_json['results'][i]['name'] for i in range(len(artist_json['results']))]
	return(song_list,artist_json)    
    
def get_songid(cid,song_name,artist_name):
	#Gets song id from Jamendo database

	#Gets list of songs by artist and the artist data
	song_list,artist_json = get_song_list(cid,artist_name) 

	#Finds index of song title in list
	for i in range(len(song_list)):     
		if song_list[i] == song_name:
			y = i
			break
    
	#Finds and returns jamendo song id in artist json
	song_id = artist_json['results'][y]['id'] 
	return(song_id)

def get_song(cid,song_name,artist_name):
	#Downloads mp3 of song

	#Gets song_id
	song_id = get_songid(cid,song_name,artist_name)  
	url = "https://api.jamendo.com/v3.0/tracks/file/?client_id="+str(cid)+"&id="+str(song_id)+"&action=download"
	#Names downloaded file, as of now downloads to desktop
	cwd = os.getcwd()
	fname = str(cwd) + "/music/" + str(artist_name)+" - "+str(song_name)+".mp3" 

	#Downloads song 
	content = requests.get(url, stream=True).content   
	with open(fname, 'wb') as f:
		f.write(content)
	return mp3_to_wav(fname)	

def mp3_to_wav(in_fname):
	#Converts mp3 to wav file, saves new file in same place
	sound = AudioSegment.from_mp3(in_fname)
	sound.export(in_fname[:-3] + "wav", format="wav")
	return in_fname[:-3] + "wav"
    
def wav_analyzer_fft(fname,threshold):
	#Analyzes wav file

	#Reads in wav file, singles out on mono files from stereo input
	rate, data = scipy.io.wavfile.read(fname)
	signal = data[:,0]   
	#Creates window for considering small portions
	w = rate//10
	len_sig = int(len(signal)//w)

	#Loops through signal, takes fft of each window, adds to list of ffts
	wind = []
	wind_prev = []
	wind_ffts = []
	for i in range(len_sig):
		for j in range((i*w),((i*w)+w)):
			wind += [signal[j]]
			wind_prev += [signal[j]]
		if i == len_sig - 1:
			if len(wind_prev) == len(wind):
				wind_ffts += [np.fft.fft(wind)]
				wind = []
		else:
			wind_ffts += [np.fft.fft(wind)]
			wind = []
    
	#Creates list(returns list in seconds) of places in song where there is some significant frequency difference
	plan = []
	for i in range(1,len(wind_ffts)):
		if (sum(wind_ffts[i] - wind_ffts[i-1])/sum(wind_ffts[i-1])) * 100 > threshold:
			plan += [i*w]
	plan_sec = [plan[i]/44100 for i in range(0,len(plan))]
	return plan_sec

def play_song(fname,song_ready,color_ready):
	#Plays song

	#Readies song and color for multiprocessing
	song_ready.set() 
	color_ready.wait()

	#time,wait(some time) <= if necessary to sync 
	chunk = 1024
	wf = wave.open(fname, 'rb')
	p = pyaudio.PyAudio()
	#Opens stream
	stream = p.open(
		format = p.get_format_from_width(wf.getsampwidth()),
		channels = wf.getnchannels(),
		rate = wf.getframerate(),
		output = True)
	data = wf.readframes(chunk)
	#Plays data/audio
	while data != '': 
		stream.write(data)
		data = wf.readframes(chunk)
		#Closes stream after song finishes
	stream.close()
	p.terminate()
    
def mainRun(fname,threshold):
	#Main function for playing song and running light visualization 

	#Creates plan_sec from wav_analyzer
	plan_sec = wav_analyzer_fft(fname,threshold)

	#Preps multiprocessing events for each function
	color_ready = multiprocessing.Event()
	song_ready = multiprocessing.Event()   
	#Begins each separate event, runs both functions in sync
	songProcess = multiprocessing.Process(target=play_song,args = (fname, song_ready, color_ready))
	songProcess.start()  
	lights.setColor_v2(plan_sec,color_ready,song_ready)
	
if __name__ == "__main__":
	mainRun(sys.argv[1],95)
