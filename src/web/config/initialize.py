"""initialize.py
    holds all the state variables for our taipy app
"""

import configparser
import os
import sys

BASE_URL = "https://api.genius.com"

def get_config_file():
    # Get settings from the user's thoughtbubble.conf file if it exists
    config = configparser.ConfigParser()
    try:
        config.read(os.path.expanduser("config/thoughtbubble.conf"))
    except configparser.MissingSectionHeaderError as e:
        print("Invalid thoughtbubble.conf file: Missing [thoughtbubble] header.")
        sys.exit(1)
    return config

def get_access_token():
    # Set variables from config
    return get_config_file()["thoughtbubble"]["access_token"]

def get_limit():
    if get_config_file()["thoughtbubble"]["limit"]:
        return int(get_config_file()["thoughtbubble"]["limit"])
    else:   
        return 50