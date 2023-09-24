from taipy.gui import Markdown

songs_md = Markdown("""
<|layout|columns=10vw 1 10vw|gap=20px|class_name=align-columns-top
<|part
|>
<top|part|render={songs_data.empty is not True}
<|Songs by {artist_data.loc[0]['name']}|text|class_name=h5 mb2 mt2|>
<|{songs_data}|table|page_size=10|filter=True|columns=title;release_date_for_display;stats_pageviews|show_all=False|class_name=mt1|>
|top>
<|part
|>
|>""")
