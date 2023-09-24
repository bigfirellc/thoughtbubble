from pandas import json_normalize
from config.initialize import get_access_token
from lyricsgenius import Genius

def get_artist_data(state):
    genius = Genius(get_access_token())
    genius.retries = 3
    genius.timeout = 10
    genius.response_format = 'plain'

    artist = genius.artist(state.selected_artist)['artist']

    return json_normalize(artist, sep="_")
