# thoughtbubble

A simple python CLI that creates a PNG wordcloud from a specified artist name. thoughtbubble queries the genius.com API. 

## installation

Installation is less than difficult. It works on Ubuntu Linux, not sure about anything else at the moment.

Clone the repository or download the zip and unpack it

```bash
git clone https://github.com/nqnzp/thoughtbubble
```

Create a virtualenv

```bash
# Python 2
virtualenv venv/
. venv/bin/activate

# Python 3
python3 -m venv venv/.
. venv/bin/activate
```

In your venv, run pip to install it

```bash
pip install --editable .
```

And now you can run the dang thing

```bash
thoughtbubble "weezer"
```

Default output is a PNG file named thoughtbubble.png. You can also specify a different name for the output file
by evoking thoughtbubble with some arguments
```bash
thoughtbubble "Van Halen" hagar.png
```
CLI output isn't that fancy. Sometimes, genius.com has a hard time figuring out what
the name of the artist is you are searching for, so thoughtbubble returns a list of
all the artists genius thinks it might be and gives you a choice

```bash
thoughtbubble "spoon" mycamera.png
                             
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
Scraping lyrics from genius.com
  [████████████████████████████████████]             
Making the wordcloud.
Word cloud written to mycamera.png.
```

## Wordclouds

Wordclouds at the moment are small and non-configurable. Repeated words in songs are stripped out, as are song section
tags specified in genius like `[Chorus]` and `[Verse]`.

For example, here is a wordcloud output called `sad.png`, which is the result when you run `thoughtbubble "Radiohead"`.

![](sad.png)

## Acknowledgements

This project uses some really nice code written by other people to do something dirty.

* [Click](https://github.com/pallets/click)
* [word_cloud](https://github.com/amueller/word_cloud)
