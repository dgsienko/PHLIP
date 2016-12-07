# README 
This is the repository for the CS 411 (Group 4) project, P.H.L.I.P. Read on for Documentation.

## Overview
Philips Hue Light Interface Program, or _P.H.L.I.P._, aims to help you do more with Philip Hue lights. We currently have two modes: Weather Alerts and Audio Visualizer.

### Weather Alerts
A user sets up an account with his location and can then set up a bunch of weather-based rules. For example, "turn the lights yellow for a minute at sunrise," or "flash the lights red for 30 seconds when the temperature goes above 90°F."

### Audio Visualizer
A user chooses a song from Jamendo to play, and, via audio analysis and light scheduling, the song is played with an accompanying audio visualization using the Hue lights.  
 

## Depenedencies
Our project requires the following packages/technologies be installed:
* [Node.js](https://nodejs.org/en/)
* [hue-cli](https://github.com/bahamas10/hue-cli)
* [APScheduler](https://apscheduler.readthedocs.io/)
* [Flask](http://flask.pocoo.org)
* [MySQL](http://www.mysql.com)
* [Flask-MySQL](https://flask-mysql.readthedocs.io/en/latest/)
* [NumPy](http://www.numpy.org)
* [SciPy](https://www.scipy.org)
* [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
* [Pydub](http://pydub.com)
* [FFmpeg](https://ffmpeg.org)
* [PortAudio](http://portaudio.com)

## Technologies
Our project is a **Thin Client**, using **Flask/Python** and **MySQL**. We used the Flask-MySQL combination because we were more familiar with it than with our alternatives. Having a Thin Client makes sense because, especially in the case of Weather Alerts, the website only needs to be available to manage rules -- the lights can update in the background (the computation is handled on the back-end). 