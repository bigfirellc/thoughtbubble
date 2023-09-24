from config.initialize import get_access_token, get_limit
from lyricsgenius import Genius

def get_lyrics_data(state):
    genius = Genius(get_access_token())
    genius.retries = 3
    genius.timeout = 10
    genius.response_format = 'plain'
    genius.skip_non_songs = True
    genius.excluded_terms = ["(Remix)", "(Live)"]
    genius.response_format = 'plain'
    genius.remove_section_headers = True

    state.lyrics_count = 0
    limit = get_limit()
    lyrics_df = state.songs_data.loc[:limit]
    lyrics_df['lyrics'] = str()

    for index, row in lyrics_df.iterrows():
        lyrics = genius.lyrics(song_url=row['url'])
        lyrics_df.loc[index, 'lyrics'] = lyrics
        state.lyrics_count = index
        state.lyrics_perc = int((index/limit) * 100)

    lyrics_df['lyrics'].fillna("", inplace=True)
    return lyrics_df