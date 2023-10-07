from taipy.gui import Markdown, Html


artist_md = Markdown("""
<|layout|columns=10vw 320px 1 10vw|gap=20px|class_name=align-columns-top

<|part
|>
<|part|class_name=align-item-top|render={artist_data.empty is not True}
<|About {artist_data.loc[0]['name']}|text|class_name=h5 mb1 mt2|>
|>
<|part
|>
<|part
|>

<|part
|>
<|part|class_name=align-item-top|render={artist_data.empty is not True}
<|{artist_data.loc[0]['image_url']}|image|width=320px|>
|>
<|part|class_name=align-item-top|render={artist_data.empty is not True}
<|{artist_data.loc[0]['description_html']}|>
|>
<|part
|>
|>""")
