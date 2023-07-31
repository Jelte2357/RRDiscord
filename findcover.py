import pylast
from datetime import datetime, date
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Set your Spotify API credentials
client_id = '37fb1fbfd4364a35bcfd60e8b74dba5b'
client_secret = '3fcb3937d794414db2e5fd7f085e27fc'

# Create a Spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def album_cover_spotify(artist_name, track_name):
    # Search for the track
    results = spotify.search(q=f'artist:{artist_name} track:{track_name}', type='track')

    if results['tracks']['items']:
        # Get the first track's album
        album = results['tracks']['items'][0]['album']

        # Get the album cover URL
        if album['images']:
            cover_url = album['images'][0]['url']
            return cover_url
        else:
            return None
    else:
        return None

API_KEY = "8c7727fc6cd50b476d7d18779a5a1973"
API_SECRET = "971fbadbc121391120a1147159bb6118"
USERNAME = "radiorijks"

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

def album_cover_lastfm(artist, title):
    global network
    try:
        track = network.get_track(artist, title)
        album = track.get_album()
        images = album.get_cover_image()
        return images
    except:
        return None

def album_cover(title, artist, ReTry=None):
  if ReTry == True:
    lsttitle = [title[:title.find(string)] for string in ['[', '(', '{', '!'] if string in title]
    lstartist = [artist[:artist.find(string)] for string in ['[', '(', '{', '!'] if string in title]
    for artist in lstartist:
      for title in lsttitle:
        song = album_cover(artist, title)
        if song:
          return song
    return None

  Albumcover=album_cover_spotify(artist, title)
  if Albumcover != None:
    return Albumcover
  else:
    Albumcover=album_cover_lastfm(artist,title)
    if Albumcover!=None:
      return Albumcover
    else:
      return album_cover(artist, title, ReTry=True)
