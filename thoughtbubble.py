# -*- coding: utf-8 -*-
# thoughbubble.py

import click
import configparser
import json
import nltk
nltk.download('stopwords')
nltk.download('punkt')
import pandas as pd
import os
import requests
import sys
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from tqdm import tqdm
from wordcloud import WordCloud, STOPWORDS

version = "thoughtbubble 0.2.0"
base_url = "https://api.genius.com"


def get_artist(artist, access_token):

    search_url = base_url + "/search"
    param_payload = {'q': artist, 'access_token': access_token}
    
    r = requests.get(search_url, params=param_payload)
    a = json.loads(r.content)

    click.secho(f"\nSearching Genius for \"{artist}\".", fg='yellow')

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
        click.secho("\nGenius is terrible at searching artist names!", fg='red')
        click.secho("Select an artist from the results it returned:", fg='red')
        i = 0
        for item in l:
            click.echo(f"[{str(i + 1)}]", nl=False)
            click.secho(f" {item[0]}", fg='yellow')
            i += 1
        num = input('Enter a number [1-' + str(i) + ']: ')
        num = int(num) - 1
        artist_name = l[num][0]
        artist_id = l[num][1]
    else:
        click.secho(f"\nSuccessfully found {l[0][0]} on Genius!", fg='green')
        artist_name = l[0][0]
        artist_id = l[0][1]

    if not (artist_name):
        click.echo("Unable to find an artist with that name.")
        sys.exit(1)
    else:
        return artist_name, artist_id

def get_songs(artist_name, artist_id, access_token, limit):

    click.secho(f"\nDownloading data for the {str(limit)} most popular songs by {artist_name}.", fg='yellow')

    headers = {'Authorization': 'Bearer ' + access_token}
    search_url = base_url + "/artists/" + str(artist_id) + "/songs"
    per_page = limit / (limit / 10)
    param_payload = {'per_page': per_page, 'page': 1, 'sort': "popularity"}
    pagination = limit / param_payload['per_page']

    pbar = tqdm(total = int(pagination * per_page), colour = 'GREEN')
    while param_payload['page'] <= pagination:

        r = requests.get(search_url, params=param_payload, headers=headers)
        data = json.loads(r.text)

        if param_payload['page'] == 1:
            songs_df = pd.json_normalize(data['response']['songs'], sep='_')
        else:
            temp_df = pd.json_normalize(data['response']['songs'], sep='_')
            songs_df = pd.concat([songs_df, temp_df], ignore_index=True)

        param_payload['page'] += 1
        pbar.update(int(1 * per_page))
    
    pbar.close()
    songs_df = songs_df[songs_df.primary_artist_name == artist_name]

    return songs_df

def get_lyrics(songs_df):

    click.secho(f"\nDownloading lyrics.", fg='yellow')

    for index, row in tqdm(songs_df.iterrows(), total=songs_df.shape[0], colour = 'GREEN'):
        page_url = "http://genius.com" + row['api_path']
        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, 'lxml')
        soup_div = soup.find('div', class_="Lyrics__Container-sc-1ynbvzw-5 Dzxov")

        if soup_div is not None:
            chunk = soup_div.get_text(" ")
            songs_df.loc[index, 'lyrics'] = chunk
        else:
            songs_df.loc[index, 'lyrics'] = ""

    return songs_df

def make_word_cloud(songs_df, artist_name, filename):

    click.secho(f"\nCleaning up the data set.", fg='yellow')

    # Converting words to lowercase
    songs_df['lyrics'] = songs_df['lyrics'].apply(lambda x: x.lower() if isinstance(x, str) else x)

    # Removing non word and non whitespace characters
    songs_df['lyrics'] = songs_df['lyrics'].replace(to_replace=r'[^\w\s]', value='', regex=True)

    # Removing digits
    songs_df['lyrics'] = songs_df['lyrics'].replace(to_replace=r'\d', value='', regex=True)

    # Tokenizing
    songs_df['lyrics'] = songs_df['lyrics'].apply(word_tokenize)
    
    # Setting some stopwords
    stop_words = set(stopwords.words('english'))
    stop_words.update(set(STOPWORDS))
    stop_words.update(word_tokenize(artist_name.lower()))
    stop_words.update(["chorus", "bridge", "verse", "intro", "outro", "solo",
                        "guitar", "refrain", "lyric"])

    # Removing NLTK and other stopwords
    songs_df['lyrics'] = songs_df['lyrics'].apply(lambda x: [word for word in x if word not in stop_words])

    wc = WordCloud(max_words=100,
                   width=800,
                   height=600,
                   min_word_length=3,
                   collocations=True,
                   font_path="./Inconsolata.otf")

    click.secho("\nMaking the word cloud.", fg='yellow')

    # Yikes!
    lyrics = ' '.join(sum(songs_df['lyrics'].to_list(),[]))

    wc.generate(lyrics)
    wc.to_file(filename)

    click.secho(f"\nWord cloud written to \"{filename}\"!\n", fg='green')

    return songs_df


@click.command()
@click.argument('artist', type=str)
@click.argument('filename', default="", type=click.Path(exists=False))
def cli(artist, filename):

    click.secho(f"\n{version}", fg='green', bold=True)
    click.secho(f"https://github.com/lesservehicle/thoughtbubble", fg='blue')

    # Get settings from the user's thoughtbubble.conf file if it exists
    config = configparser.ConfigParser()
    try:
        config.read(os.path.expanduser('thoughtbubble.conf'))
    except configparser.MissingSectionHeaderError as e:
        click.echo("Invalid thoughtbubble.conf file: Missing [thoughtbubble] header.")
        sys.exit(1)

    # Set variables from config
    access_token = config["thoughtbubble"]["access_token"]
    
    if config["thoughtbubble"]["limit"]:
        limit = int(config["thoughtbubble"]["limit"])
    else:
        limit = 50
    
    # Get the correct artist name by performing a search
    try:
        artist_name, artist_id = get_artist(artist, access_token)
    except KeyError as e:
        click.echo(e)
        sys.exit(1)

    try:
        songs_df = get_songs(artist_name, artist_id, access_token, limit)
    except KeyError as e:
        click.echo(e)
        sys.exit(1)

    try:
        songs_df = get_lyrics(songs_df)
    except KeyError as e:
        click.echo(e)
        sys.exit(1)

    if filename == "":
        filename = f"{artist_name}.png"

    try:
        songs_df = make_word_cloud(songs_df, artist_name, filename)
    except KeyError as e:
        click.echo(e)
        sys.exit(1)

if __name__ == '__main__':
    cli()