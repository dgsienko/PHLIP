#Audio Import and Analysis

import requests
from pydub import AudioSegment
import numpy as np
import scipy.io.wavfile
import pyaudio
import wave
import time
from multiprocessing import Process
import random


#fname = "Jekk - First.wav"
#threshold = 60

def get_song_list(cid,artist_name):
    #gets list of songs from input artist
    
    #following three lines make api call and get back dictionary of all songs (and data from songs) by the artist
    url = "https://api.jamendo.com/v3.0/tracks/?client_id="+str(cid)+"&artist_name="+artist_name
    response = requests.get(url)
    artist_json = response.json()
    
    #makes a list of all songs by the artist
    song_list = [artist_json['results'][i]['name'] for i in range(len(artist_json['results']))]
    
    return(song_list,artist_json)    
    
def get_songid(song_name):
    #gets song id from Jamendo database
    
    #gets list of songs by artist and the artist data
    song_list,artist_json = get_song_list(cid,artist_name) 
    
    #finds index of song title in list
    for i in range(len(song_list)):     
        if song_list[i] == song_name:
            y = i
            break
    
    #finds jamendo song id in artist json
    song_id = artist_json['results'][y]['id'] 
    
    return(song_id)

def get_song():
    #Downloads mp3 of song
    
    #gets song_id
    song_id = get_songid(song_name)  
    url = "https://api.jamendo.com/v3.0/tracks/file/?client_id="+str(cid)+"&id="+str(song_id)+"&action=download"
    #names downloaded file, as of now downloads to desktop
    fname = str(artist_name)+" - "+str(song_name)+".mp3"  
    
    #downloads song 
    content = requests.get(url, stream=True).content   
    with open(fname, 'wb') as f:
        f.write(content)
        
def mp3_to_wav(in_fname):
    #converts mp3 to wav file
    
    #convert to wav
    sound = AudioSegment.from_mp3(in_fname)
    sound.export(in_fname[:-3] + "wav", format="wav")  
    
def wav_analyzer(fname):
    #audio analyzer
    
    #reads in wav file given filename
    rate, data = scipy.io.wavfile.read(fname)
    signal = data[:,0]
    convert_to_16 = float(2**15)
    signal = abs(signal/(float(2**15)+1.0))
    
    #if first value is not zero, add to plan
    plan = []
    if signal[0] != 0:
        plan += [0]
     
    #creates plan for lights/list of index values in samples
    for i in range(1,len(signal)):
        if ((signal[i] - signal[i-1]) / signal[i-1]) * 100 == 70:
            plan += [i]
            
    #convert list values to seconds
    plan_sec = [plan[i]/44100 for i in range(0,len(plan))]
    #print(len(plan_sec))
    return plan_sec

def randomHex():
    hexVal = ["0000FF","FF0000","800080","00FFEC","00EA00"]
    choice = random.choice(hexVal)
    return choice

def setColor(plan_sec):
    for i in range(1,len(plan_sec)):
        #os.system('hue lights all ' + randomHex())
        print(randomHex())
        time.sleep(plan_sec[i]-plan_sec[i-1])

def play_song(fname):
    #plays song
    
    chunk = 1024
    wf = wave.open(fname, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(
        format = p.get_format_from_width(wf.getsampwidth()),
        channels = wf.getnchannels(),
        rate = wf.getframerate(),
        output = True)
    data = wf.readframes(chunk)

    while data != '': 
        stream.write(data)
        data = wf.readframes(chunk)

    stream.close()
    p.terminate()
    
def mainRun(fname):
    plan_sec = wav_analyzer(fname)

    p2 = Process(target=setColor(plan_sec))
    p1 = Process(target=play_song(fname))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
