from flask import Flask, request, url_for, session, redirect, render_template, render_template_string
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

    def clear_cache(self):
        session.pop(TOKEN_INFO, None)

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return render_template('login.html')

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
    return render_template('choose_action.html')

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
        print(f"Fetching songs with offset {iteration * 50}")
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
        items = sp.current_user_top_tracks(limit=10, offset=iteration * 50)["items"]
        iteration += 1
        top_tracks += items
        if(len(top_tracks) > 50):
            break
    
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
        if(len(top_tracks) > 50):
            break

    top_track_ids = [track['id'] for track in top_tracks]
    
    recommendations = sp.recommendations(seed_tracks=top_track_ids[:5], limit=20)["tracks"]
    
    formatted_recommendations = []
    for track in recommendations:
        track_name = track['name']
        artists = ', '.join(artist['name'] for artist in track['artists'])
        formatted_recommendations.append(f"{track_name} by {artists}")
    
    return "<br>".join(formatted_recommendations)

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

    playlist = sp.user_playlist_create(
        user=user_id, 
        name=playlist_name, 
        public=is_public, 
        collaborative=is_collaborative, 
        description=playlist_description
    )

    session['playlist_id'] = playlist['id']

    return "Playlist created successfully!"

@app.route('/swipeRecommendations')
def swipeRecommendations():
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
        if(iteration >= 50):
            break

    top_track_ids = [track['id'] for track in top_tracks]
    
    recommendations = sp.recommendations(seed_tracks=top_track_ids[:5], limit=20)["tracks"]
    
    return render_template('swipe_recommendations.html', recommendations=recommendations)

@app.route('/swipeAction', methods=['POST'])
def swipeAction():
    if request.method == 'POST':
        action = request.form['action']
        track_uri = request.form['track_uri']
        if action == 'Like':
            try:
                token_info = get_token()
            except:
                print("User not logged in")
                return redirect("/")
            
            sp = spotipy.Spotify(auth=token_info["access_token"])
            playlist_id = session.get('playlist_id')
            if playlist_id:
                sp.user_playlist_add_tracks(user=sp.me()['id'], playlist_id=playlist_id, tracks=[track_uri])
            print(f"Liked: {track_uri}")
        elif action == 'Dislike':
            print(f"Disliked: {track_uri}")
    return redirect('/swipeRecommendations')

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())

    is_expired = token_info["expires_at"] - now < 60
    if(is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session[TOKEN_INFO] = token_info
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id= client_id,
        client_secret= client_secret,
        redirect_uri=url_for('redirectPage', _external=True),
        scope="user-library-read user-top-read playlist-modify-public playlist-modify-private",
        cache_handler=CustomCacheHandler()
    )