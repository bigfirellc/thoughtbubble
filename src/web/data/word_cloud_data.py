import nltk
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud, STOPWORDS

def make_word_cloud(state):
    """Makes a word cloud from lyrics_data, saves it to FILENAME

    Args:
        state (Taipy state object): The state of the application with global variables
    """

    nltk.download("stopwords", quiet=True)
    nltk.download("punkt", quiet=True)

    clean_df = state.lyrics_data

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
    stop_words.update(word_tokenize(state.artist_data.loc[0, 'name'].lower()))
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
    word_cloud_lyrics = " ".join(sum(clean_df["lyrics"].to_list(), []))

    word_cloud = WordCloud(
        width=1920,
        height=1080,
        min_word_length=4,
        collocations=False,
        font_path="./fonts/Roboto-Regular.ttf",
    )
    word_cloud.generate(word_cloud_lyrics)

    word_cloud_filename = f"assets/{state.artist_data.loc[0]['name']}.png"
    word_cloud.to_file(word_cloud_filename)

    return word_cloud_filename




