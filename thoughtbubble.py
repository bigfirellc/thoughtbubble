# -*- coding: utf-8 -*-
# https://bigishdata.com/2016/09/27/getting-song-lyrics-from-geniuss-api-scraping/
# http://www.compjour.org/warmups/govt-text-releases/intro-to-bs4-lxml-parsing-wh-press-briefings/

import click
from os import path
from wordcloud import WordCloud, STOPWORDS
import requests
import configparser
import os
import sys
import json
from bs4 import BeautifulSoup

base_url = "https://api.genius.com"
version = "thoughtbubble 0.1.0"

def make_word_cloud(text, artist, filename):

    stopwords = set(STOPWORDS)
    stopwords.add(artist)
    stopwords.add("Chorus")
    stopwords.add("Verse")
    stopwords.add("Bridge")
    stopwords.add("Guitar Solo")
    stopwords.add("Outro")
    stopwords.add("Intro")

    wc = WordCloud(background_color="white",
                   max_words=500,
                   width=800,
                   height=600,
                   stopwords=stopwords,
                   max_font_size=80,
                   min_font_size=10,
                   font_path="./Inconsolata.otf")

    click.echo("Making the word cloud.")

    wc.generate(text)
    wc.to_file(filename)
    click.echo("Word cloud written to " + filename + ".\n")


def text_from_genius(artist, access_token):
    search_url = base_url + "/search"
    param_payload = {'q': artist, 'access_token': access_token}
    headers = {'Authorization': 'Bearer ' + access_token}

    r = requests.get(search_url, params=param_payload)
    a = json.loads(r.content)

    click.echo("Searching genius.com for \"" + artist + "\".\n")

    l = list() # a list of tuples
    for hit in a["response"]["hits"]:
        # make a tuple, add it to the list
        t = (hit["result"]["primary_artist"]["name"], hit["result"]["primary_artist"]["id"])
        l.append(t)

    myset = set(l)
    l = list(myset)

    if len(l) > 1:
        click.echo("Genius.com is terrible at searching artist names.")
        click.echo("Select an artist from the results it returned:")
        i = 0
        for item in l:
            click.echo("[" + str(i + 1) + "] " + item[0])
            i += 1
        num = input('Enter a number[1-' + str(i) + ']: ')
        num = int(num) - 1
        artist_name = l[num][0]
        artist_id = l[num][1]
    else:
        artist_name = l[0][0]
        artist_id = l[0][1]

    if not (artist_name):
        click.echo("Unable to find an artist with that name.")
        sys.exit(1)

    click.echo("Generating a word cloud with lyrics from the top 20 songs by " + artist_name + ".")

    search_url = base_url + "/artists/" + str(artist_id) + "/songs"
    r = requests.get(search_url, headers=headers)
    s = json.loads(r.content)

    lyrics = ""

    click.echo("Fetching lyrics from genius.com.")

    with click.progressbar(s["response"]["songs"], show_percent=False,
                           fill_char=click.style(u'█', fg='green')) as bar:
        for hit in bar:
            page_url = "http://genius.com" + hit["path"]
            page = requests.get(page_url)

            soup = BeautifulSoup(page.text, 'lxml')

            ignore_list = ("[Bridge]","[Chorus]","[Guitar]","[Guitar Solo]",
                           "[Instrumental]","[Outro]","[Verse]", artist_name)

            chunk = soup.find('div', class_="lyrics").text
            chunk = chunk.replace('\n', ' ').replace('\r', '')
            chunk = ' '.join(unique_list(chunk.split()))
            lyrics += chunk

    return lyrics

def unique_list(l):
    ulist = []
    [ulist.append(x) for x in l if x not in ulist]
    return ulist

@click.command()
@click.argument('artist', type=str)
@click.argument('filename', default="thoughtbubble.png", type=click.Path(exists=False))
def cli(artist, filename):

    click.echo(version)

    # Get things from the user's .wezzer file if they exist
    config = configparser.ConfigParser()
    try:
        config.read(os.path.expanduser('thoughtbubble.conf'))
    except configparser.MissingSectionHeaderError as e:
        click.echo("Invalid thoughtbubble.conf file: Missing [thoughtbubble] header.")
        sys.exit(1)

    try:
        text = text_from_genius(artist, config["thoughtbubble"]["access_token"])
    except KeyError as e:
        click.echo("Missing/invalid thoughtbubble.conf file or access_token parameter.")
        click.echo("Go to https://genius.com/api-clients, get a Client Access Token, and")
        click.echo("copy it into thoughtbubble.conf.")
        sys.exit(1)

    make_word_cloud(text, artist, filename)


if __name__ == '__main__':
    cli()