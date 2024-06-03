# german's file

from flask import Flask, request, url_for, session, redirect
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

app.secret_key = "8fhkslfmpio4pa98"
app.config['SESSION_COOKIE_NAME'] = 'Beach Cookie'

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    return "redirect"

@app.route('/getTracks')
def getTracks():
    return "User top songs"

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id= "194564bfd0694b6c85aef9f8182616eb",
        client_secret= "bf2ca6fa80af4a5e86dff533018a79b7",
        redirect_uri=url_for('redirectPage', _external=True),
        scope="user-library-read"
    )
