"""thoughtbubble Taipy app
"""
from taipy.gui import Gui
from pages import root_md, artist_md, albums_md, songs_md, lyrics_md, word_cloud_md
import pandas as pd

artist_search = None
selector_artists = []
selected_artist = None
artist_data = pd.DataFrame()
albums_data = pd.DataFrame()
songs_data = pd.DataFrame()
lyrics_data = pd.DataFrame()
lyrics_count = 0
lyrics_perc = 0
word_cloud_filename = None

pages = {
    "/": root_md,
    "artist": artist_md,
    "albums": albums_md,
    "songs": songs_md,
    "lyrics": lyrics_md,
    "wordcloud": word_cloud_md
}

stylekit = {
    "input_button_height": "56px"
}

gui = Gui(pages=pages)


if __name__ == '__main__':
    gui.run(
        css_file="main.css",
        run_in_thread=True,
        title="thoughtbubble",
        dark_mode=True,
        margin=None,
        watermark="",
        stylekit=stylekit,
        use_reloader=True,
        debug=False,
        notebook_proxy=False,
        single_client=False
    )
