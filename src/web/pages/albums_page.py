from taipy.gui import Markdown

albums_md = Markdown("""
<|layout|columns=10vw 1 10vw|gap=20px|class_name=align-columns-top
<|part
|>
<|{albums_data}|table|page_size=10|filter=True|columns=name;release_date_for_display;stats_pageviews|show_all=False|class_name=mt1|>
|>
<|part
|>
""")
