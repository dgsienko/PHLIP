#Audio Import and Analysis

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
    
def wav_analyzer_fft(fname,threshold):
    
    rate, data = scipy.io.wavfile.read(fname)
    signal = data[:,0]
     
    w = rate//10
    len_sig = int(len(signal)//w)
        
    blah = []
    blah_prev = []
    blah_ffts = []
    for i in range(len_sig):
        for j in range((i*w),((i*w)+w)):
            blah += [signal[j]]
            blah_prev += [signal[j]]
        if i == len_sig - 1:
            if len(blah_prev) == len(blah):
                blah_ffts += [np.fft.fft(blah)]
                blah = []
        else:
            blah_ffts += [np.fft.fft(blah)]
            blah = []
    
    plan = []
    for i in range(1,len(blah_ffts)):
        if (sum(blah_ffts[i] - blah_ffts[i-1])/sum(blah_ffts[i-1])) * 100 > threshold:
            plan += [i*w]
    
    plan_sec = [plan[i]/44100 for i in range(0,len(plan))]
    return plan_sec

def play_song(fname,song_ready,color_ready):
    #plays song

    song_ready.set() 
    color_ready.wait()
    
    #time,wait(some time) <= if necessary to sync
    
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
    
def mainRun(fname,threshold):
    plan_sec = wav_analyzer_fft(fname,threshold)
    
    color_ready = multiprocessing.Event()
    song_ready = multiprocessing.Event()
    
    songProcess = multiprocessing.Process(target=play_song,args = (fname, song_ready, color_ready))
    songProcess.start()
    
    setColor_v2(plan_sec,color_ready,song_ready)
