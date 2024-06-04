#chris file

from dotenv import load_dotenv
import os
import base64
import requests
from requests import post
import json 
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time 
from flask import Flask, request, url_for, session, redirect



load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

#print (client_id)
#print (client_secret)

def get_token():
    token_info = session.get(TOKEN_INFO,None)
    if not token_info:
        raise "exception"
    now = int(time.time())

    is_expired = token_info["expires_at"] - now < 60
    if(is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info["refresh_tokem"])
    return token_info

token = get_token()
print(token)



