from taipy.gui import Markdown

word_cloud_md = Markdown("""
<|layout|columns=10vw 1 10vw|gap=20px|class_name=align-columns-top
<|part
|>
<lyrics|part|render={lyrics_count > 0}
<|Retrieving Lyrics for {lyrics_count} Songs by {artist_data.loc[0]['name']}|text|class_name=h5 mb1 mt2|>
<|{lyrics_perc}%|indicator|value={lyrics_perc}|min=0|max=100|width=100%|>
|lyrics>
<image|part|render={word_cloud_filename is not None}
<|Word Cloud|text|class_name=h5 mb2 mt2|>
<|{word_cloud_filename}|image|width=100%|>
|image>
<|part
|>
|>""")
