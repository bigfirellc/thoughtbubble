from pandas import json_normalize
from config.initialize import get_access_token
from lyricsgenius import Genius

def get_songs_data(state):
    genius = Genius(get_access_token())
    genius.retries = 3
    genius.timeout = 10
    genius.response_format = 'plain'
    genius.skip_non_songs = True
    genius.excluded_terms = ["(Remix)", "(Live)"]
    genius.response_format = 'plain'
    
    page = 1
    songs = []
    while page:
        request = genius.artist_songs(int(state.artist_data.loc[0]['id']),
                                    sort='popularity',
                                    per_page=50,
                                    page=page)
        page = request['next_page']
        songs.extend(request['songs'])

    return json_normalize(songs, sep="_")