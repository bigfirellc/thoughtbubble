from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from taipy.gui import Gui, Icon, notify
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
from wordcloud import WordCloud, STOPWORDS
import pandas as pd
import thoughtbubble as tb
import configparser
import json
import os
import requests
import sys
import time

# initializing state variables
access_token = None
artist_df = None
artist_name = None
artist_id = None
base_url = "https://api.genius.com"
error = None
filename = None
header = None
limit = None
lyrics_df = None
search = None
top10_sel = None
songs_df = None
top10_lov = list()
top10_df = pd.DataFrame(columns=['thumbnail', 'link', 'title'])
version = "thoughtbubble 0.2.0"

# Get settings from the user's thoughtbubble.conf file if it exists
config = configparser.ConfigParser()
try:
    config.read(os.path.expanduser('thoughtbubble.conf'))
except configparser.MissingSectionHeaderError as e:
    print("Invalid thoughtbubble.conf file: Missing [thoughtbubble] header.")
    sys.exit(1)

# Set variables from config
access_token = config["thoughtbubble"]["access_token"]

if config["thoughtbubble"]["limit"]:
    limit = int(config["thoughtbubble"]["limit"])
else:
    limit = 50


def get_artist(state):

    notify(state, "info", f"Searching for \"{state.search}\"...")

    search_url = state.base_url + "/search"
    param_payload = {'q': state.search, 'access_token': state.access_token}
    artist_name = None
    artist_id = None
    
    r = requests.get(search_url, params=param_payload)
    a = json.loads(r.content)

    l = list()  # a list of tuples
    for hit in a["response"]["hits"]:
        # make a tuple, add it to the list
        t = (
                hit["result"]["primary_artist"]["name"], 
                hit["result"]["primary_artist"]["id"]
            )
        l.append(t)

    myset = set(l)
    l = list(myset)

    if len(l) > 1:
        for item in l:
            if item[0].lower() == state.search.lower():
                artist_name = item[0]
                artist_id = item[1]
    elif l is None:
        notify(state, "error", f"Artist \"{state.search}\" not found!")                   
        return None, None
    else:
        artist_name = l[0][0]
        artist_id = l[0][1]
    
    if not (artist_name):
        notify(state, "error", f"Artist \"{state.search}\" not found!")                   
        return None, None
    else:
        notify(state, "success", f"Artist \"{artist_name}\" found!")
        return artist_name, artist_id


def get_songs(state):

    notify(state, "info", "Getting song info...")

    headers = {'Authorization': 'Bearer ' + state.access_token}
    search_url = state.base_url + "/artists/" + str(state.artist_id) + "/songs"
    per_page = state.limit / (state.limit / 10)
    param_payload = {'per_page': per_page, 'page': 1, 'sort': "popularity"}
    pagination = state.limit / param_payload['per_page']

    # Looping through each page of the request
    while param_payload['page'] <= pagination:

        r = requests.get(search_url, params=param_payload, headers=headers)
        data = json.loads(r.text)

        if param_payload['page'] == 1:
            songs_df = pd.json_normalize(data['response']['songs'], sep='_')
        else:
            temp_df = pd.json_normalize(data['response']['songs'], sep='_')
            songs_df = pd.concat([songs_df, temp_df], ignore_index=True)

        param_payload['page'] += 1
        
    # Removing songs that don't match the artist name
    songs_df = songs_df[songs_df.primary_artist_name == state.artist_name]
    songs_df.drop(columns=['featured_artists'], inplace=True)

    notify(state, "success", f"Song info for {state.artist_name} found!")

    state.songs_df = songs_df
    
    # Make the DataFrame for the top 10 songs list
    
    top10_df = songs_df[0:9]
    state.top10_lov = [] 

    for index, row in top10_df.iterrows():
        state.top10_lov.append((str(index), Icon(row['song_art_image_thumbnail_url'], row['title'])))
        
    state.header = top10_df.loc[0, 'header_image_url']
    state.top10_df = top10_df
    state.refresh('songs_df')
    state.refresh('top10_df')
    state.refresh('top10_lov')


def get_lyrics(state):

    notify(state, "info", f"Getting lyrics for {state.artist_name}...")

    lyrics_df = state.songs_df

    for index, row in lyrics_df.iterrows():
        page_url = "http://genius.com" + row['api_path']
        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, 'lxml')
        soup_div = soup.find('div', class_="Lyrics__Container-sc-1ynbvzw-5 Dzxov")

        if soup_div is not None:
            chunk = soup_div.get_text(" ")
            lyrics_df.loc[index, 'lyrics'] = chunk
        else:
            lyrics_df.loc[index, 'lyrics'] = ""                     

    notify(state, "success", f"Lyrics retrieved!")

    state.lyrics_df = lyrics_df


def make_word_cloud(state):

    notify(state, "info", f"Cleaning up lyrics...")

    clean_df = state.lyrics_df

    # Converting words to lowercase
    clean_df['lyrics'] = clean_df['lyrics'].apply(lambda x: x.lower() if isinstance(x, str) else x)

    # Removing non word and non whitespace characters
    clean_df['lyrics'] = clean_df['lyrics'].replace(to_replace=r'[^\w\s]', value='', regex=True)

    # Removing digits
    clean_df['lyrics'] = clean_df['lyrics'].replace(to_replace=r'\d', value='', regex=True)

    # Tokenizing
    clean_df['lyrics'] = clean_df['lyrics'].apply(word_tokenize)
    
    # Setting some stopwords
    stop_words = set(nltk.corpus.stopwords.words('english'))
    stop_words.update(set(STOPWORDS))
    stop_words.update(word_tokenize(state.artist_name.lower()))
    stop_words.update(["chorus", "bridge", "verse", "intro", "outro", "solo",
                        "guitar", "refrain", "lyric", "prechorus", "instrumental"])

    # Removing NLTK and other stopwords
    clean_df['lyrics'] = clean_df['lyrics'].apply(lambda x: [word for word in x if word not in stop_words])
    
    # Convert all of the lyrics rows in our Dataframe to a single list
    lyrics = ' '.join(sum(clean_df['lyrics'].to_list(),[]))

    notify(state, "info", f"Making word cloud...")

    wc = WordCloud(width=800, height=600, min_word_length=4, collocations=False, font_path="./Roboto-Regular.ttf")
    wc.generate(lyrics)

    filename = f"assets/{state.artist_name}.png"
    wc.to_file(filename)
    state.filename = filename
    state.refresh('filename')



def on_click(state):

    state.artist_name, state.artist_id = get_artist(state)
    
    if state.artist_name is not None and state.artist_id is not None:
        get_songs(state)
        get_lyrics(state)
        make_word_cloud(state)

# Definition of the page
page = """
# thoughtbubble # {: .h1}

<|{search}|input|>

<|go|button|on_action=on_click|>

<artist|part|render={artist_name is not None}
<|{artist_name}|text|class_name=h2|raw=True|>
|artist>

<|layout|

<topten|part|render={top10_df.empty is not True}
### Top 10 Songs on Genius ### {: .h3}
<|{top10_sel}|tree|lov={top10_lov}|>
|topten>

<image|part|render={filename is not None}
### Word Cloud ### {: .h3}
<|{filename}|image|height=600px|width=800px|>
|image>

|>
"""

Gui(page).run(title="thoughtbubble", dark_mode=False)