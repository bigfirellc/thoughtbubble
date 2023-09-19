"""
thoughtbubble is a module that instantiates a command line client
to search the Genius.com API for artists and return a word cloud

"""
import os
import sys
import json
import configparser
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud, STOPWORDS
import click

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)

VERSION = "thoughtbubble 0.2.0"
BASE_URL = "https://api.genius.com"


def get_artist(artist, access_token, quiet=False):
    """
    Returns the result of an artist search in the Genius API

            Parameters:
                    artist (str): A search query for an artist
                    access_token (str): Genius API Access Token
                    quiet (bool): Suppress commandline output

            Returns:
                    artist_name (str): Search result of artist name
                    artist_id (int): The artist's ID in Genius
    """

    search_url = BASE_URL + "/search"
    param_payload = {"q": artist, "access_token": access_token}
    artist_name = None
    artist_id = None
    genius_request = requests.get(search_url, params=param_payload, timeout=300)
    genius_answer = json.loads(genius_request.content)

    if not quiet:
        click.secho(f'\nSearching Genius for "{artist}".', fg="yellow")

    genius_list = [] # a list of tuples
    for hit in genius_answer["response"]["hits"]:
        # make a tuple, add it to the list
        genius_tuple = (
            hit["result"]["primary_artist"]["name"],
            hit["result"]["primary_artist"]["id"],
        )
        genius_list.append(genius_tuple)

    genius_list = list(set(genius_list))

    if len(genius_list) > 1:
        click.secho("\nGenius is terrible at searching artist names!", fg="red")
        click.secho("Select an artist from the results it returned:", fg="red")
        for item in genius_list:
            if item[0].lower() == artist.lower():
                artist_name = item[0]
                artist_id = item[1]
        iterator = 0
        for item in genius_list:
            click.echo(f"[{str(iterator + 1)}]", nl=False)
            click.secho(f" {item[0]}", fg="yellow")
            iterator += 1
        num = input("Enter a number [1-" + str(iterator) + "]: ")
        num = int(num) - 1
        artist_name = genius_list[num][0]
        artist_id = genius_list[num][1]

    elif genius_list is None:
        if not quiet:
            click.secho(f'\nArtist "{artist}" not found!', fg="red")
        return None, None
    else:
        if not quiet:
            click.secho(
                f"\nSuccessfully found {genius_list[0][0]} on Genius!", fg="green"
            )
        artist_name = genius_list[0][0]
        artist_id = genius_list[0][1]

    if artist_name:
        return artist_name, artist_id

    if not quiet:
        click.secho(f'\nArtist "{artist}" not found!', fg="red")
    return None, None


def get_songs(artist_name, artist_id, access_token, limit, quiet=False):
    """
    Returns the result of a search in the Genius API for songs by a specified artist

            Parameters:
                    artist_name (str): Artist's name
                    artist_id (str): Artist's ID in Genius
                    access_token (str): Genius API Access Token
                    limit (int): Number of songs returned
                    quiet (bool): Suppress commandline output

            Returns:
                    songs_df (Dataframe): Songs and attached metadata
    """

    if not quiet:
        click.secho(
            f"\nDownloading data for the {str(limit)} most popular songs by {artist_name}.",
            fg="yellow",
        )

    headers = {"Authorization": "Bearer " + access_token}
    search_url = BASE_URL + "/artists/" + str(artist_id) + "/songs"
    per_page = limit / (limit / 10)
    param_payload = {"per_page": per_page, "page": 1, "sort": "popularity"}
    pagination = limit / param_payload["per_page"]

    # Setting up a progress bar with TQDM
    if not quiet:
        pbar = tqdm(total=int(pagination * per_page), colour="GREEN")

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
        if not quiet:
            pbar.update(int(1 * per_page))

    if not quiet:
        pbar.close()

    # Removing songs that don't match the artist name
    songs_df = songs_df[songs_df.primary_artist_name == artist_name]
    songs_df.drop(columns=["featured_artists"], inplace=True)

    return songs_df


def get_lyrics(songs_df, quiet=False):
    """
    Returns the result of a search in the Genius API for lyrics by a specified artist

            Parameters:
                    songs_df (Dataframe): Songs and attached metadata
                    quiet (bool): Suppress commandline output

            Returns:
                    songs_df (Dataframe): Songs and attached metadata
    """
    if not quiet:
        click.secho("\nDownloading lyrics.", fg="yellow")

    if not quiet:
        for index, row in tqdm(
                songs_df.iterrows(), total=songs_df.shape[0], colour="GREEN"
        ):
            page_url = "http://genius.com" + row["api_path"]
            page = requests.get(page_url, timeout=300)
            soup = BeautifulSoup(page.content, "lxml")
            soup_div = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-5 Dzxov")

            if soup_div is not None:
                chunk = soup_div.get_text(" ")
                songs_df.loc[index, "lyrics"] = chunk
            else:
                songs_df.loc[index, "lyrics"] = ""
    else:
        for index, row in songs_df.iterrows():
            page_url = "http://genius.com" + row["api_path"]
            page = requests.get(page_url, timeout=300)
            soup = BeautifulSoup(page.content, "lxml")
            soup_div = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-5 Dzxov")

            if soup_div is not None:
                chunk = soup_div.get_text(" ")
                songs_df.loc[index, "lyrics"] = chunk
            else:
                songs_df.loc[index, "lyrics"] = ""

    return songs_df


def make_word_cloud(songs_df, artist_name, filename, quiet=False):
    """
    Outputs a word cloud from the Dataframe to the specified filename

            Parameters:
                    songs_df (Dataframe): Songs and attached metadata
                    artist_name (str): Artist's name
                    filename (str): Where to write the word cloud
                    quiet (bool): Suppress commandline output

            Returns:
                    songs_df (Dataframe): Songs and attached metadata
    """
    if not quiet:
        click.secho("\nCleaning up the data set.", fg="yellow")

    # Converting words to lowercase
    songs_df["lyrics"] = songs_df["lyrics"].apply(
        lambda x: x.lower() if isinstance(x, str) else x
    )

    # Removing non word and non whitespace characters
    songs_df["lyrics"] = songs_df["lyrics"].replace(
        to_replace=r"[^\w\s]", value="", regex=True
    )

    # Removing digits
    songs_df["lyrics"] = songs_df["lyrics"].replace(
        to_replace=r"\d", value="", regex=True
    )

    # Tokenizing
    songs_df["lyrics"] = songs_df["lyrics"].apply(word_tokenize)

    # Setting some stopwords
    stop_words = set(nltk.corpus.stopwords.words("english"))
    stop_words.update(set(STOPWORDS))
    stop_words.update(word_tokenize(artist_name.lower()))
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
        ]
    )

    # Removing NLTK and other stopwords
    songs_df["lyrics"] = songs_df["lyrics"].apply(
        lambda x: [word for word in x if word not in stop_words]
    )

    # Convert all of the lyrics rows in our Dataframe to a single list
    lyrics = " ".join(sum(songs_df["lyrics"].to_list(), []))

    wordcloud = WordCloud(
        width=800,
        height=600,
        min_word_length=4,
        collocations=False,
        font_path="./Roboto-Regular.ttf",
    )

    if not quiet:
        click.secho("\nMaking the word cloud.", fg="yellow")

    wordcloud.generate(lyrics)
    wordcloud.to_file(filename)

    if not quiet:
        click.secho(f'\nWord cloud written to "{filename}"!\n', fg="green")

    return songs_df


@click.command()
@click.argument("artist", type=str)
@click.argument("filename", default="", type=click.Path(exists=False))
def cli(artist, filename):
    """
    Returns the result of a search in the Genius API for songs by a specified artist

            Parameters:
                    artist_name (str): Artist's name
                    artist_id (str): Artist's ID in Genius
                    access_token (str): Genius API Access Token
                    limit (int): Number of songs returned

            Returns:
                    songs_df (Dataframe): Songs and attached metadata
    """
    click.secho(f"\n{VERSION}", fg="green", bold=True)
    click.secho("https://github.com/lesservehicle/thoughtbubble", fg="blue")

    # Get settings from the user's thoughtbubble.conf file if it exists
    config = configparser.ConfigParser()
    try:
        config.read(os.path.expanduser("thoughtbubble.conf"))
    except configparser.MissingSectionHeaderError as config_error:
        click.echo(
            f"Invalid thoughtbubble.conf file: Missing [thoughtbubble] header. {config_error}"
        )
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
    except KeyError as key_error:
        click.echo(key_error)
        sys.exit(1)

    try:
        songs_df = get_songs(artist_name, artist_id, access_token, limit)
    except KeyError as key_error:
        click.echo(key_error)
        sys.exit(1)

    try:
        songs_df = get_lyrics(songs_df)
    except KeyError as key_error:
        click.echo(key_error)
        sys.exit(1)

    if filename == "":
        filename = f"{artist_name}.png"

    filename = f"assets/{filename}"

    try:
        songs_df = make_word_cloud(songs_df, artist_name, filename)
    except KeyError as key_error:
        click.echo(key_error)
        sys.exit(1)


if __name__ == "__main__":
    cli()
