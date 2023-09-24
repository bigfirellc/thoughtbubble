from taipy.gui import Markdown, Icon, notify
from data.artist_data import get_artist_data
from data.albums_data import get_albums_data
from data.songs_data import get_songs_data
from data.lyrics_data import get_lyrics_data
from data.word_cloud_data import make_word_cloud
from config.initialize import get_access_token
from lyricsgenius import Genius


def on_search_button(state):
    """Action taken upon clicking the button under the search field

    Args:
        state (Taipy state object): The state of the application with global variables
    """
    state.selector_artists = []
    state.refresh("selector_artists")

    genius = Genius(get_access_token())
    genius.retries = 3
    genius.timeout = 10
    genius.response_format = 'plain'

    notify(state, "info", f'Searching for "{state.artist_search}"...')

    search_results = genius.search_artists(state.artist_search)

    if len(search_results['sections'][0]['hits']) > 0:
        for hit in search_results['sections'][0]['hits']:
            result = hit['result']
            state.selector_artists.append((str(result['id']), Icon(result['image_url'], result['name'])))

        state.refresh("selector_artists")
    else:
        notify(state, "error", f"Can't find anything matching \"{state.artist_search}\"!")


def on_select_button(state):
    """Action taken upon choosing an item from the selector field

    Args:
        state (Taipy state object): The state of the application with global variables
    """    
    state.artist_data = get_artist_data(state)
    notify(state, "success", f"Artist {state.artist_data.loc[0]['name']} found!")
    state.albums_data = get_albums_data(state)
    notify(state, "success", f"Albums for {state.artist_data.loc[0]['name']} found!")
    state.songs_data = get_songs_data(state)
    notify(state, "success", f"Songs for {state.artist_data.loc[0]['name']} found!")
    notify(state, "info", f"Getting lyrics for {state.artist_data.loc[0]['name']}...")
    state.lyrics_data = get_lyrics_data(state)
    notify(state, "success", f"Lyrics for {state.artist_data.loc[0]['name']} found!")
    notify(state, "info", f"Making a word cloud for {state.artist_data.loc[0]['name']}...")
    state.lyrics_count = 0
    state.word_cloud_filename = make_word_cloud(state)
    notify(state, "success", f"Word cloud for {state.artist_data.loc[0]['name']} done!")

root_md = Markdown("""
<|layout|columns=10vw 1 10vw|class_name=align-columns-top header

<|part
|>
<|part|
<|thoughtbubble|text|class_name=h1 mt1|>
<|insights about artists|text|class_name=h6 mb2|>
|>
<|part
|>
|>

<|layout|columns=10vw 240px 100px 240px 100px 1 10vw|class_name=align-columns-top header

<|part
|>
<|part|class_name=mb1
<|{artist_search}|input|class_name=align-item-top m0|action_keys=Enter|on_action=on_search_button|label=enter an artist|> 
|>
<|part|class_name=mb1
<|Search|button|class_name=align-item-top|on_action=on_search_button|>
|>
<|part|render={len(selector_artists) > 0}
<|{selected_artist}|selector|class_name=align-item-top m0 p0|lov={selector_artists}|dropdown=True|value_by_id=True|label=select an artist|id=searchselector|>
|>
<|part|render={len(selector_artists) > 0}
<|Select|button|class_name=align-item-top|on_action=on_select_button|>
|>
<|part|class_name=mb1
|>
<|part|class_name=mb1
|>
|>

<|layout|columns=10vw 1 10vw|gap=20px|class_name=align-columns-top
<|part
|>
<artist|part|render={artist_data.empty is not True}
<|{artist_data.loc[0]['name']}|text|class_name=h3 mt2|>
|artist>
<|part
|>
|>

<|part|render={artist_data.empty is not True}
<center><|navbar|></center>
|>
""")