from setuptools import setup

setup(
    name='thoughtbubble',
    version='0.1',
    py_modules=['thoughtbubble'],
    install_requires=[
        'wordcloud',
        'Click',
        'requests',
        'configparser',
        'bs4',
        'lxml'
    ],
    entry_points='''
        [console_scripts]
        thoughtbubble=thoughtbubble:cli
    ''',
)