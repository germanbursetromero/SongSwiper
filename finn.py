import json
import time
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import requests
from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
load_dotenv()

#_______________German oauth code________
app = Flask(__name__)

app.secret_key = "8fhkslfmpio4pa98"
app.config['SESSION_COOKIE_NAME'] = 'Beach Cookie'
app.config['SERVER_NAME'] = 'localhost:5000'  # Set the SERVER_NAME configuration
TOKEN_INFO = "token_info"

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('chooseAction', _external=True))

@app.route('/chooseAction')
def chooseAction():
    return """
        <h1>Choose an action:</h1>
        <ul>
            <li><a href="/getTracks">View Saved Tracks</a></li>
            <li><a href="/getTopTracks">View Top Tracks</a></li>
        </ul>
    """

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info["access_token"])
    all_songs = []
    iteration = 0
    while True:
        items = sp.current_user_saved_tracks(limit=50, offset=iteration * 50)["items"]
        iteration += 1
        all_songs += items
        if(len(items) < 50):
            break
    
    limited_songs = all_songs[:50]
    formatted_songs = []

    for song in limited_songs:
        track = song['track']
        track_name = track['name']
        artists = ', '.join(artist['name'] for artist in track['artists'])
        formatted_songs.append(f"{track_name} by {artists}")

    return "<br>".join(formatted_songs)

@app.route('/getTopTracks')
def getTopTracks():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info["access_token"])
    top_tracks = []
    iteration = 0
    while True:
        items = sp.current_user_top_tracks(limit=10, offset=iteration * 10)["items"]
        iteration += 1
        top_tracks += items
        if(len(items) < 50):
            break
    
    formatted_tracks = []
    for track in top_tracks:
        track_name = track['name']
        artists = ', '.join(artist['name'] for artist in track['artists'])
        formatted_tracks.append(f"{track_name} by {artists}")

    return "<br>".join(formatted_tracks)

def  makeAPlaylist():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info["access_token"])
    
    user_id = input("what is your username: ")
    playlist_name = input("what would you like your playlist to be called: ")
    public = bool(input("Would you like to make your playlist public: (True/False)"))
    collaborative = bool(input("Would you like your playlist to be collaborative: (True/False)"))
    description = input("What would you like you playlist description to be: ")

    sp.user_playlist_create(user_id, playlist_name, public, collaborative, description)
    

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())

    is_expired = token_info["expires_at"] - now < 60
    if(is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id= "194564bfd0694b6c85aef9f8182616eb",
        client_secret= "bf2ca6fa80af4a5e86dff533018a79b7",
        redirect_uri=url_for('redirectPage', _external=True),
        scope="user-library-read"
    )
makeAPlaylist()
