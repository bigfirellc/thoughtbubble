"""thoughtbubble Taipy app
"""
import configparser
import json
import os
import sys
import requests
import nltk
import pandas as pd
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from taipy.gui import Gui, Icon, notify
from wordcloud import WordCloud, STOPWORDS

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)

# initializing state variables
ACCESS_TOKEN = None
ARTIST_NAME = None
ARTIST_ID = None
BASE_URL = "https://api.genius.com"
FILENAME = None
HEADER = None
LIMIT = None
LYRICS_DF = None
SEARCH = None
TOP10_SEL = None
SONGS_DF = None
TOP10_LOV = []
TOP10_DF = pd.DataFrame(columns=["thumbnail", "link", "title"])


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


def get_artist(state):
    """Finds an artist in the Genius API

    Args:
        state (Taipy state object): The state of the application with global variables
    """

    notify(state, "info", f'Searching for "{state.SEARCH}"...')

    search_url = state.BASE_URL + "/search"
    param_payload = {"q": state.SEARCH, "access_token": state.ACCESS_TOKEN}
    artist_name = None
    artist_id = None

    genius_request = requests.get(search_url, params=param_payload, timeout=300)
    genius_answer = json.loads(genius_request.content)

    genius_list = []  # a list of tuples
    for hit in genius_answer["response"]["hits"]:
        # make a tuple, add it to the list
        genius_tuple = (
            hit["result"]["primary_artist"]["name"],
            hit["result"]["primary_artist"]["id"],
        )
        genius_list.append(genius_tuple)

    genius_list = list(set(genius_list))

    if len(genius_list) > 1:
        for item in genius_list:
            if item[0].lower() == state.SEARCH.lower():
                artist_name = item[0]
                artist_id = item[1]
    elif genius_list is None:
        notify(state, "error", f'Artist "{state.SEARCH}" not found!')
        return None, None
    else:
        artist_name = genius_list[0][0]
        artist_id = genius_list[0][1]

    if artist_name:
        notify(state, "success", f'Artist "{artist_name}" found!')
        return artist_name, artist_id

    notify(state, "error", f'Artist "{state.SEARCH}" not found!')
    return None, None


def get_songs(state):
    """Gets songs from Genius API

    Args:
        state (Taipy state object): The state of the application with global variables
    """

    notify(state, "info", "Getting song info...")

    headers = {"Authorization": "Bearer " + state.ACCESS_TOKEN}
    search_url = state.BASE_URL + "/artists/" + str(state.ARTIST_ID) + "/songs"
    per_page = state.LIMIT / (state.LIMIT / 10)
    param_payload = {"per_page": per_page, "page": 1, "sort": "popularity"}
    pagination = state.LIMIT / param_payload["per_page"]

    # Looping through each page of the request
    while param_payload["page"] <= pagination:
        request = requests.get(
            search_url, params=param_payload, headers=headers, timeout=300
        )
        data = json.loads(request.text)

        if param_payload["page"] == 1:
            songs_df = pd.json_normalize(data["response"]["songs"], sep="_")
        else:
            temp_df = pd.json_normalize(data["response"]["songs"], sep="_")
            songs_df = pd.concat([songs_df, temp_df], ignore_index=True)

        param_payload["page"] += 1

    # Removing songs that don't match the artist name
    songs_df = songs_df[songs_df.primary_artist_name == state.ARTIST_NAME]
    songs_df.drop(columns=["featured_artists"], inplace=True)

    notify(state, "success", f"Song info for {state.ARTIST_NAME} found!")

    state.SONGS_DF = songs_df

    # Make the DataFrame for the top 10 songs list

    top10_df = songs_df[0:9]
    state.TOP10_LOV = []

    for index, row in top10_df.iterrows():
        state.TOP10_LOV.append(
            (str(index), Icon(row["song_art_image_thumbnail_url"], row["title"]))
        )

    state.HEADER = top10_df.loc[0, "header_image_url"]
    state.TOP10_DF = top10_df
    state.refresh("songs_df")
    state.refresh("top10_df")
    state.refresh("top10_lov")


def get_lyrics(state):
    """Gets lyrics from Genius API

    Args:
        state (Taipy state object): The state of the application with global variables
    """

    notify(state, "info", f"Getting lyrics for {state.ARTIST_NAME}...")

    lyrics_df = state.SONGS_DF

    for index, row in lyrics_df.iterrows():
        page_url = "http://genius.com" + row["api_path"]
        page = requests.get(page_url, timeout=300)
        soup = BeautifulSoup(page.content, "lxml")
        soup_div = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-5 Dzxov")

        if soup_div is not None:
            chunk = soup_div.get_text(" ")
            lyrics_df.loc[index, "lyrics"] = chunk
        else:
            lyrics_df.loc[index, "lyrics"] = ""

    notify(state, "success", "Lyrics retrieved!")

    state.LYRICS_DF = lyrics_df


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
        width=800,
        height=600,
        min_word_length=4,
        collocations=False,
        font_path="./Roboto-Regular.ttf",
    )
    wordcloud.generate(lyrics)

    filename = f"assets/{state.ARTIST_NAME}.png"
    wordcloud.to_file(filename)
    state.FILENAME = filename
    state.refresh("filename")


def on_click(state):
    """Action taken upon clicking the button under the search field

    Args:
        state (Taipy state object): The state of the application with global variables
    """
    state.ARTIST_NAME, state.ARTIST_ID = get_artist(state)

    if state.ARTIST_NAME is not None and state.ARTIST_ID is not None:
        get_songs(state)
        get_lyrics(state)
        make_word_cloud(state)


# Definition of the page
PAGE = """
# thoughtbubble # {: .h1}

<|{SEARCH}|input|>

<|go|button|on_action=on_click|>

<artist|part|render={ARTIST_NAME is not None}
<|{ARTIST_NAME}|text|class_name=h2|raw=True|>
|artist>

<|layout|

<topten|part|render={TOP10_DF.empty is not True}
### Top 10 Songs on Genius ### {: .h3}
<|{TOP10_SEL}|tree|lov={top10_lov}|>
|topten>

<image|part|render={FILENAME is not None}
### Word Cloud ### {: .h3}
<|{FILENAME}|image|height=600px|width=800px|>
|image>

|>
"""

Gui(PAGE).run(title="thoughtbubble", dark_mode=False)
