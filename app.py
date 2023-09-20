"""thoughtbubble Taipy app
"""
import configparser
import os
import sys
import nltk
from lyricsgenius import Genius
import pandas as pd
from nltk.tokenize import word_tokenize
from taipy.gui import Gui, Icon, notify
from wordcloud import WordCloud, STOPWORDS

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)

# initializing state variables
ACCESS_TOKEN = None
ARTIST_ALT = None
ARTIST_DESC = None
ARTIST_DF = pd.DataFrame()
ARTIST_ID = None
ARTIST_IMAGE = None
ARTIST_NAME = None
ARTIST_URL = None
BASE_URL = "https://api.genius.com"
FILENAME = None
HEADER = None
LIMIT = None
LYRICS_COUNT = None
LYRICS_DF = None
LYRICS_PERC = None
SEARCH = None
SEARCH_LOV = []
SEARCH_SEL = None
SONGS_DF = pd.DataFrame(columns=['title', 'release_date_for_display', 'stats_pageviews'])
TOP10_SEL = None
TOTAL_SONGS = None

# Get settings from the user's thoughtbubble.conf file if it exists
config = configparser.ConfigParser()
try:
    config.read(os.path.expanduser("thoughtbubble.conf"))
except configparser.MissingSectionHeaderError as e:
    print("Invalid thoughtbubble.conf file: Missing [thoughtbubble] header.")
    sys.exit(1)

# Set variables from config
ACCESS_TOKEN = config["thoughtbubble"]["access_token"]

if config["thoughtbubble"]["limit"]:
    LIMIT = int(config["thoughtbubble"]["limit"])
else:
    LIMIT = 50


def make_word_cloud(state):
    """Makes a word cloud from LYRICS_DF, saves it to FILENAME

    Args:
        state (Taipy state object): The state of the application with global variables
    """

    notify(state, "info", "Cleaning up lyrics...")

    clean_df = state.LYRICS_DF

    # Converting words to lowercase
    clean_df["lyrics"] = clean_df["lyrics"].apply(
        lambda x: x.lower() if isinstance(x, str) else x
    )

    # Removing non word and non whitespace characters
    clean_df["lyrics"] = clean_df["lyrics"].replace(
        to_replace=r"[^\w\s]", value="", regex=True
    )

    # Removing digits
    clean_df["lyrics"] = clean_df["lyrics"].replace(
        to_replace=r"\d", value="", regex=True
    )

    # Tokenizing
    clean_df["lyrics"] = clean_df["lyrics"].apply(word_tokenize)

    # Setting some stopwords
    stop_words = set(nltk.corpus.stopwords.words("english"))
    stop_words.update(set(STOPWORDS))
    stop_words.update(word_tokenize(state.ARTIST_NAME.lower()))
    stop_words.update(
        [
            "chorus",
            "bridge",
            "verse",
            "intro",
            "outro",
            "solo",
            "guitar",
            "refrain",
            "lyric",
            "prechorus",
            "instrumental",
        ]
    )

    # Removing NLTK and other stopwords
    clean_df["lyrics"] = clean_df["lyrics"].apply(
        lambda x: [word for word in x if word not in stop_words]
    )

    # Convert all of the lyrics rows in our Dataframe to a single list
    lyrics = " ".join(sum(clean_df["lyrics"].to_list(), []))

    notify(state, "info", "Making word cloud...")

    wordcloud = WordCloud(
        width=1920,
        height=1080,
        min_word_length=4,
        collocations=False,
        font_path="./Roboto-Regular.ttf",
    )
    wordcloud.generate(lyrics)

    filename = f"assets/{state.ARTIST_NAME}.png"
    wordcloud.to_file(filename)

    state.LYRICS_COUNT = None
    state.refresh("LYRICS_COUNT")
    state.FILENAME = filename
    state.refresh("FILENAME")


def on_search_button(state):
    """Action taken upon clicking the button under the search field

    Args:
        state (Taipy state object): The state of the application with global variables
    """
    state.SEARCH_LOV = []
    state.refresh("SEARCH_LOV")
    state.TOTAL_SONGS = None
    state.refresh("TOTAL_SONGS")

    genius = Genius(state.ACCESS_TOKEN)
    genius.retries = 3
    genius.timeout = 10
    genius.remove_section_headers = True
    genius.skip_non_songs = True
    genius.excluded_terms = ["(Remix)", "(Live)"]
    genius.response_format = 'plain'

    notify(state, "info", f'Searching for "{state.SEARCH}"...')

    search_results = genius.search_artists(state.SEARCH)

    if len(search_results['sections'][0]['hits']) > 0:
        for hit in search_results['sections'][0]['hits']:
            result = hit['result']
            state.SEARCH_LOV.append((str(result['id']), Icon(result['image_url'], result['name'])))

        state.refresh("SEARCH_LOV")
    else:
        notify(state, "error", f"Can't find anything matching \"{state.SEARCH}\"!")


def on_select_button(state):
    """Action taken upon clicking the button under the select field

    Args:
        state (Taipy state object): The state of the application with global variables
    """
    genius = Genius(state.ACCESS_TOKEN)
    genius.retries = 3
    genius.timeout = 10
    genius.remove_section_headers = True
    genius.skip_non_songs = True
    genius.excluded_terms = ["(Remix)", "(Live)"]
    genius.response_format = 'plain'

    artist = genius.artist(state.SEARCH_SEL)['artist']

    notify(state, "success", f"Artist {artist['name']} found!")
    state.HEADER = artist['header_image_url']
    state.ARTIST_IMAGE = artist['image_url']
    state.ARTIST_NAME = artist['name']
    state.ARTIST_DESC = artist['description']['plain']
    state.ARTIST_URL = artist['url']

    state.refresh("ARTIST_DESC")

    if artist['alternate_names']:
        state.ARTIST_ALT = ", ".join(artist['alternate_names'])

    notify(state, "info", f"Pulling information about {artist['name']}...")
    state.ARTIST_DF = pd.json_normalize(artist, sep="_")

    notify(state, "info", f"Pulling songs from {artist['name']}...")

    page = 1
    songs = []

    while page:
        request = genius.artist_songs(int(artist['id']),
                                    sort='popularity',
                                    per_page=50,
                                    page=page)
        page = request['next_page']
        songs.extend(request['songs'])

    state.SONGS_DF = pd.json_normalize(songs, sep="_")
    state.refresh("SONGS_DF")

    notify(state, "info", f"Getting lyrics for {state.ARTIST_NAME}...")

    lyrics_df = state.SONGS_DF
    state.LYRICS_COUNT = 0
    state.TOTAL_SONGS = int(len(songs))

    for song in enumerate(songs):
        lyrics_df.loc[song[0], "lyrics"] = genius.lyrics(song_url=song[1]['url'])
        state.LYRICS_COUNT = state.LYRICS_COUNT + 1
        state.LYRICS_PERC = int((state.LYRICS_COUNT/state.TOTAL_SONGS) * 100)

    notify(state, "success", "Done!")

    state.LYRICS_DF = lyrics_df
    state.LYRICS_DF['lyrics'].fillna("", inplace=True)


    make_word_cloud(state)

# Definition of the page
PAGE = """

<header|part|
<|thoughtbubble|text|class_name=h1|>
<|insights about artists|text|class_name=h6 mb2|>
|header>

<|layout|columns=320px 128px

<searchinput|part
<|{SEARCH}|input|class_name=d-inline|action_keys=Enter|> 
|searchinput>
<searchbutton|part
<|Search|button|on_action=on_search_button|>
|searchbutton>

<selector|part|render={len(SEARCH_LOV) != 0}
<|{SEARCH_SEL}|selector|class_name=d-inline|lov={SEARCH_LOV}|dropdown=True|value_by_id=True|>
|selector>
<selectbutton|part|render={len(SEARCH_LOV) != 0}
<|Select|button|on_action=on_select_button|>
|selectbutton>

|>

<artist|part|render={ARTIST_NAME is not None}
<|{ARTIST_NAME}|text|class_name=h3 mt2|>
<|insights about {ARTIST_NAME}|text|class_name=h6 mb2|>
|artist>

<|layout|class_name=align-columns-top|gap=32px|columns=320px 1
<|part|class_name=align-item-top|render={ARTIST_IMAGE is not None}
<|{ARTIST_IMAGE}|image|width=320px|>
|>
<|part|class_name=align-item-top|render={ARTIST_DESC is not None}
<|{ARTIST_DESC}|text|raw=True|>
|>
|>

<top|part|render={SONGS_DF.empty is not True}
<|Top songs by {ARTIST_NAME}|text|class_name=h5 mb1 mt2|>
<|{SONGS_DF}|table|page_size=10|filter=True|columns=title;release_date_for_display;stats_pageviews|show_all=False|class_name=mt1|>
|top>

<lyrics|part|render={LYRICS_COUNT is not None}
<|Retrieving Lyrics for {LYRICS_COUNT} Songs by {ARTIST_NAME}|text|class_name=h5 mb1 mt2|>
<|{LYRICS_PERC}%|indicator|value={LYRICS_PERC}|min=0|max=100|width=90vw|>
|lyrics>

<image|part|render={FILENAME is not None}
<|Word Cloud|text|class_name=h5 mb1 mt2|>
<|{FILENAME}|image|width=100%|>
|image>
"""

stylekit = {
    "input_button_height":"64px",
    "border_radius":"0px",
    "font_family":"Roboto"
}

pages = {
    "/": "",
    "main_page": PAGE,
}

Gui(pages=pages).run(
    run_in_thread=True,
    title="thoughtbubble",
    stylekit=stylekit,
    dark_mode=True,
    margin=None,
    watermark="",
    use_reloader=True,
    debug=True,
    notebook_proxy=False,
    single_client=True
)
