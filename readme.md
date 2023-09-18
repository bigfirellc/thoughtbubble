# thoughtbubble

A simple Python commandline tool that creates a PNG word cloud from a specified artist name, querying the [Genius API.](https://docs.genius.com)

## Installation

Clone the repository somewhere nice and change to the new directory you've just created.

```
git clone https://github.com/lesservehicle/thoughtbubble.git
cd thoughtbubble
```

Install [pipenv](https://pipenv.pypa.io/en/latest/installation/) if you don't have it already.

```bash
pip install pipenv
```

Use `pipenv` to install the dependencies and create a new virtual environment.

```bash
pipenv install .
```

Use `pipenv shell` to open the new virtual environment.

```
% pipenv shell
Launching subshell in virtual environment...
 . /Users/adam/.local/share/virtualenvs/thoughtbubble-I9oEMh-u/bin/activate
adam@compy386 thoughtbubble %  . /Users/adam/.local/share/virtualenvs/thoughtbubble-
I9oEMh-u/bin/activate
```

Your prompt should change now to let you know you are in a virtualenv to something like this:

```bash
(thoughtbubble) adam@compy386:~/thoughtbubble$
```

Now in your activated virtualenv, run pip to install thoughtbubble with setuptools:

```bash
pip install -e .
```

A copy of thoughtbubble will be made in your virtual environment and added to your  `$PATH`, so you'll be able to run it wherever you are.

If you leave your terminal and come back, you should be able to go straight to your repository directory, enable the virtual environment and run thoughtbubble.

```
cd ~/thoughtbubble
pipenv shell
thoughtbubble "Mott the Hoople"
```

## Configuration

thoughtbubble requires an API token from Genius. Make an account for yourself and generate a Client Access Token: [https://genius.com/api-clients](https://genius.com/api-clients)

Copy `thoughtbubble.conf.example` to `thoughtbubble.conf`

```bash
cp thoughtbubble.conf.example thoughtbubble.conf
```

Edit it to include your Access Token and set the query limit to whatever you like (default is 100).

```commandline
[thoughtbubble]
access_token = <your token>
limit = 100
```

And finally you can run the dang thing.

```bash
thoughtbubble "weezer"
```

If you're on macOS, you can open the image you just created with Preview. If you're on Windows or Linux, I'm sorry.

```bash
open thoughtbubble.png
```

## Usage

Simply feed thoughtbubble the name of an artist or band that you would like to create a word cloud for. Use double-quotes so it doesn't get confused.

```
thoughtbubble "Hot Water Music"
```

The default output is a PNG file named after the artist you entered, eg. `Hot Water Music.png`. You can also specify a different name for the output file by evoking thoughtbubble with an extra argument.

```bash
thoughtbubble "Van Halen" nohagar.png
```

Sometimes, Genius has a hard time figuring out what the name of the artist is that you are searching for. So, thoughtbubble will return a list of all the artists Genius thinks it might be and gives you a menu. Here is an example with a band that is named after both an eating utensil and a song by Can.

```bash
(thoughtbubble) adam@compy386 thoughtbubble % thoughtbubble "spoon"

thoughtbubble 0.2.0
https://github.com/lesservehicle/thoughtbubble

Searching Genius for "spoon".

Genius is terrible at searching artist names!
Select an artist from the results it returned:
[1] Genius English Translations
[2] Soundgarden
[3] BTS
[4] The Lovin’ Spoonful
[5] Spoon
[6] Genius Romanizations
[7] Поперечный (Poperechny)
[8] Julie Andrews
[9] Elliphant
Enter a number [1-9]: 5

Downloading data for the 100 most popular songs by Spoon.
100%|██████████████████████████████████████████████████| 100/100 [00:07<00:00, 14.24it/s]

Downloading lyrics.
100%|████████████████████████████████████████████████████| 98/98 [01:42<00:00,  1.04s/it]

Cleaning up the data set.

Making the word cloud.

Word cloud written to "Spoon.png"!
```

## Word Clouds

Word clouds at the moment are non-configurable. Future versions will allow user configuration of the font size, dimensions, and background color of the word cloud.

Repeated words in songs are stripped out, as are song section tags specified in genius like `[Chorus]` and `[Verse]` and `[Guitar Solo]`. Words are normalized to lowercase, tokenized, and stopwords are removed.

For example, here is a the output when you run `thoughtbubble "Frightened Rabbit" frabbit.png`. I'm using a cool utility called `imgcat` to be able to display the word cloud image directly in my terminal window.

![Example](example.png "Example")

## Taipy App

Thoughtbubble comes bundled with a [Taipy](https://docs.taipy.io/en/release-2.3/) app now. Install all the prerequisites as above, and run the Taipy app:

```
$ python app.py --threading
[2023-09-17 22:43:03][Taipy][INFO]  * Server starting on http://127.0.0.1:5000
```

And now you should be able to see the Taipy app in your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000). It's really rough right now. Once I smooth out the details, I'll have some more instructions on how to deploy it properly.

## Roadmap

* Fix up the Taipy app to look nice
* Migrate the backend to Taipy Core
* Migrate much of the code base to use [LyricsGenius](https://lyricsgenius.readthedocs.io/en/master/)
* Allow the user to select the limit as a commandline parameter
* Allow the user to turn off the default output coloring
* Allow user configuration of word cloud dimensions, fonts, font sizes, colors
* Multi-language support (currently english only)
* Make thoughtbubble a proper package on pypi.org to simplify the installation process
* Use pandas to output additional statistical information about the lyrics other than just word clouds

## Acknowledgements

This project wouldn't have been possible without the hard work of other much smarter developers.

* [Click](https://github.com/pallets/click)
* [word_cloud](https://github.com/amueller/word_cloud)
* [https://bigishdata.com/2016/09/27/getting-song-lyrics-from-geniuss-api-scraping/](https://bigishdata.com/2016/09/27/getting-song-lyrics-from-geniuss-api-scraping/)
* [http://www.compjour.org/warmups/govt-text-releases/intro-to-bs4-lxml-parsing-wh-press-briefings/](http://www.compjour.org/warmups/govt-text-releases/intro-to-bs4-lxml-parsing-wh-press-briefings/)
