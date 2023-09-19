"""pip install -e .
"""

from setuptools import setup

setup(
    name='thoughtbubble',
    version='0.2',
    py_modules=['thoughtbubble'],
    install_requires=[
        'wordcloud',
        'Click',
        'requests',
        'configparser',
        'bs4',
        'lxml',
        'pandas',
        'html5lib',
        'nltk',
        'tqdm',
        'Flask',
        'taipy',
        'pylint'
    ],
    entry_points='''
        [console_scripts]
        thoughtbubble=thoughtbubble:cli
    ''',
)
