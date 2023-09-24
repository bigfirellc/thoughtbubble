from pandas import json_normalize
from config.initialize import get_access_token
from lyricsgenius import Genius

def get_albums_data(state):
    genius = Genius(get_access_token())
    genius.retries = 3
    genius.timeout = 10
    genius.response_format = 'plain'

    albums = genius.artist_albums(state.artist_data.loc[0]['id'])

    albums_df = json_normalize(albums['albums'], sep='_')
    albums_df.sort_values(
        by=['release_date_components_year', 'release_date_components_month', 'release_date_components_day'], 
        ascending=False,
        inplace=True
    )

    return albums_df