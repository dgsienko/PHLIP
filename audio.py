#Audio Import and Analysis

import requests
from pydub import AudioSegment
import array
import numpy as np
import scipy.io.wavfile

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
        
def mp3_to_wav(in_fname,out_fname):
    #converts mp3 to wav file
    
    #convert to wav
    sound = AudioSegment.from_mp3(in_fname)
    sound.export(out_fname, format="wav")  
    
def wav_analyzer(fname,threshold):
    #audio analyzer
    
    #reads in wav file given filename
    rate, data = scipy.io.wavfile.read(fname)
    signal = data[:,0]
    #converst to 64 bit float
    convert_16_bit = float(2**15)
    #takes abs value and constrains within 0,1
    signal = abs(signal / (convert_16_bit + 1.0))  
    
    #if first value is not zero, add to plan
    plan = []
    if signal[0] != 0:
        plan += [0]
     
    #creates plan for lights/list of index values in samples
    for i in range(1,len(signal)):
        if ((signal[i] - signal[i-1]) / signal[i-1]) == (threshold/100):
            plan += [i]
            
    #convert list values to seconds
    plan_sec = [plan[i]/44100 for i in range(0,len(plan))]

    return plan_sec
    
