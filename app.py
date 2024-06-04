from flask import Flask, request, url_for, session, redirect, render_template_string
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import json

app = Flask(__name__)

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

app.secret_key = "8fhkslfmpio4pa98"
app.config['SESSION_COOKIE_NAME'] = 'Beach Cookie'
TOKEN_INFO = "token_info"

class CustomCacheHandler(spotipy.cache_handler.CacheHandler):
    def __init__(self):
        self.token_info = None

    def get_cached_token(self):
        return session.get(TOKEN_INFO)

    def save_token_to_cache(self, token_info):
        session[TOKEN_INFO] = token_info

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
            <li><a href="/getRecommendations">Get Recommendations</a></li>
            <li><a href="/createPlaylistForm">Create Playlist</a></li>
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
        if(iteration >= 50):
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
        items = sp.current_user_top_tracks(limit=10, offset=iteration * 50)["items"]
        iteration += 1
        top_tracks += items
<<<<<<< HEAD
        if(iteration >= 50):
=======
        if(iteration>=50):
            break
        
<<<<<<< HEAD
            
=======
>>>>>>> 90141e2b31007ada7e399579732322efd98d8cd8
            break
>>>>>>> f14cdc36e02cd5fa3fa95dd2407a7f650571364c
    
    formatted_tracks = []
    for track in top_tracks:
        track_name = track['name']
        artists = ', '.join(artist['name'] for artist in track['artists'])
        formatted_tracks.append(f"{track_name} by {artists}")

    return "<br>".join(formatted_tracks)

@app.route('/getRecommendations')
def getRecommendations():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")
    
    sp = spotipy.Spotify(auth=token_info["access_token"])
    
    top_tracks = []
    iteration = 0
    while True:
        items = sp.current_user_top_tracks(limit=10, offset=iteration * 50)["items"]
        iteration += 1
        top_tracks += items
<<<<<<< HEAD
        if(iteration) > 50:
=======
        if(iteration >= 50):
>>>>>>> f14cdc36e02cd5fa3fa95dd2407a7f650571364c
            break

    top_track_ids = [track['id'] for track in top_tracks]
    
    recommendations = sp.recommendations(seed_tracks=top_track_ids[:5], limit=20)["tracks"]
    
    formatted_recommendations = []
    for track in recommendations:
        track_name = track['name']
        artists = ', '.join(artist['name'] for artist in track['artists'])
        formatted_recommendations.append(f"{track_name} by {artists}")
    
    return "<br>".join(formatted_recommendations)
    

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
        client_id= client_id,
        client_secret= client_secret,
        redirect_uri=url_for('redirectPage', _external=True),
        scope="user-library-read user-top-read playlist-modify-public",
        cache_handler=CustomCacheHandler()
    )
@app.route('/createPlaylistForm')
def createPlaylistForm():
    form_html = """
        <h1>Create a New Playlist</h1>
        <form method="POST" action="/createPlaylist">
            <label for="name">Playlist Name:</label>
            <input type="text" id="name" name="name" required><br>
            
            <label for="description">Description:</label>
            <textarea id="description" name="description"></textarea><br>
            
            <label for="public">Public:</label>
            <input type="checkbox" id="public" name="public"><br>
            
            <label for="collaborative">Collaborative:</label>
            <input type="checkbox" id="collaborative" name="collaborative"><br>
            
            <button type="submit">Create Playlist</button>
        </form>
    """
    return render_template_string(form_html)

@app.route('/createPlaylist', methods=['POST']) 
def createPlaylist():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")

    sp = spotipy.Spotify(auth=token_info["access_token"])
    user_id = sp.me()['id']

    playlist_name = request.form['name']
    playlist_description = request.form['description']
    is_public = 'public' in request.form
    is_collaborative = 'collaborative' in request.form

    sp.user_playlist_create(
        user=user_id, 
        name=playlist_name, 
        public=is_public, 
        collaborative=is_collaborative, 
        description=playlist_description
    )

    return "Playlist created successfully!"