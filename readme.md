# thoughtbubble

A simple python CLI that creates a PNG wordcloud from a specified artist name. thoughtbubble queries the genius.com API.

## installation

Install virtualenv if you don't have it already

```bash
pip install virtualenv
```

Create a directory for the virtual environment, and activate it:

```bash
python3 -m virtualenv venv
. ~/venv/bin/activate

Your prompt should change now to let you know you are in a virtualenv
to something like this:

```bash
(venv) user@compy386:~/thoughtbubble$
```

Now in your activated virtualenv, run pip to install thoughtbubble with setuptools:

```bash
pip install --editable .
```

A copy of the CLI will be made in `./venv/bin/` and added to your
`$PATH`, so you'll be able to run it straight from where you are.

## configuration

thoughtbubble requires an API token from Genius. Make an account for yourself
and generate a Client Access Token: https://genius.com/api-clients

Copy thoughtbubble.conf.example to thoughtbubble.conf

```bash
cp thoughtbubble.conf.example thoughtbubble.conf
```

Edit it to include your Access Token

```commandline
[thoughtbubble]
access_token = <your token>
```

And finally you can run the dang thing

```bash
thoughtbubble "weezer"
```

If you're on macOS, you can open the image you just created with Preview
```bash
open thoughtbubble.png
```

## usage

The default output is a PNG file named thoughtbubble.png. You can also specify a different name for the output file
by evoking thoughtbubble with an extra argument.
```bash
thoughtbubble "Van Halen" hagar.png
```
CLI output isn't that fancy. Sometimes, genius.com has a hard time figuring out what
the name of the artist is you are searching for, so thoughtbubble will return a list of
all the artists genius thinks it might be and gives you a choice:

```bash
$ thoughtbubble "spoon" mycamera.png

thoughtbubble 0.1.0                     
Searching genius.com for "spoon".

Genius.com is terrible at searching artist names.
Select an artist from the results it returned:
[1] BTS
[2] Macklemore & Ryan Lewis
[3] Поперечный (Poperechny)
[4] Lily Allen
[5] Spoon
[6] Elliphant
Enter a number[1-6]: 5

Generating a word cloud with lyrics from the top 20 songs by Spoon.
Fetching lyrics from genius.com
  [████████████████████████████████████]
               
Making the word cloud.
Word cloud written to mycamera.png.
```

## word clouds

Word clouds at the moment are non-configurable. Future versions will allow user configuration of the font size, 
dimensions, and background color of the word cloud. 

Repeated words in songs are stripped out, as are song section
tags specified in genius like `[Chorus]` and `[Verse]` and `[Rad Solo]`.

For example, here is a wordcloud output called `frabbit.png`, which would be the result 
you run `thoughtbubble "Frightened Rabbit" frabbit.png`.

![](https://user-images.githubusercontent.com/20565648/40031261-de4d7434-57bc-11e8-9ed5-742646cbb4fd.png)

## acknowledgements

This project wouldn't have been possible without the hard work of other much smarter developers:

* [Click](https://github.com/pallets/click)
* [word_cloud](https://github.com/amueller/word_cloud)
* <https://bigishdata.com/2016/09/27/getting-song-lyrics-from-geniuss-api-scraping/>
* <http://www.compjour.org/warmups/govt-text-releases/intro-to-bs4-lxml-parsing-wh-press-briefings/>