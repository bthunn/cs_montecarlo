import json
import csv
import re
import os
import pandas as pd

def load_json(path:str):
    if not os.path.exists(path):
        raise Exception(f"Error: Failed to open JSON file, does not exist at {path}")
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def load_df_from_csv(path:str, delim:str=','):
    if not os.path.exists(path):
        raise Exception(f"Error: Failed to open CSV file, does not exist at {path}")
    with open(path, 'r', encoding='utf-8') as file:
        return pd.read_csv(path, index_col=0)
    
def replace_non_ascii(text:str, placeholder:str='?'):
    # Encode the string to bytes, ignoring errors, then decode back to string
    return text.encode('ascii', 'replace').decode().replace('?', placeholder)

def replace_invalid_chars_for_filepath(text, placeholder='-'):
    # global function for replacing characters that cant be included in file path names
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, placeholder, replace_non_ascii(text))

def replace_spaces(item_name): 
    # replaces spaces with %20
    return item_name.replace(" ", "%20")

def format_markethashname(item_name):
    # THIS IS THE FORMAT IN WHICH ITEMS ARE NAMED IN BOTH PRICE DATA FOLDERS AND DATAFRAMES
    return replace_spaces(replace_invalid_chars_for_filepath(item_name))
