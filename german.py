# german's file

from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth


app = Flask(__name__)

app.secret_key = "8fhkslfmpio4pa98"
app.config['SESSION_COOKIE_NAME'] = 'Beach Cookie'

@app.route('/')
def index():
    return "Song Swiper"

@app.route('/getTracks')
def getTracks():
    return "User top songs"
